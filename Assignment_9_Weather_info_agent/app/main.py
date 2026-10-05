from pathlib import Path
import json, os, re
from typing import Any
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()
BASE_DIR=Path(__file__).resolve().parent.parent
OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL","http://localhost:11434")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL","gemma3:4b")
app=FastAPI(title="Weather AI Agent")
app.mount("/static",StaticFiles(directory=BASE_DIR/"static"),name="static")

CODES={0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Fog",48:"Rime fog",51:"Light drizzle",53:"Moderate drizzle",55:"Dense drizzle",56:"Light freezing drizzle",57:"Dense freezing drizzle",61:"Slight rain",63:"Moderate rain",65:"Heavy rain",66:"Light freezing rain",67:"Heavy freezing rain",71:"Slight snow",73:"Moderate snow",75:"Heavy snow",77:"Snow grains",80:"Slight rain showers",81:"Moderate rain showers",82:"Violent rain showers",85:"Slight snow showers",86:"Heavy snow showers",95:"Thunderstorm",96:"Thunderstorm with hail",99:"Heavy thunderstorm with hail"}

def label(code:int)->str: return CODES.get(code,"Unknown conditions")
def icon(code:int,day:int=1)->str:
    if code==0:return "☀️" if day else "🌙"
    if code in (1,2):return "🌤️" if day else "☁️"
    if code in (3,45,48):return "☁️"
    if code in (51,53,55,56,57,61,63,65,66,67,80,81,82):return "🌧️"
    if code in (71,73,75,77,85,86):return "❄️"
    if code in (95,96,99):return "⛈️"
    return "🌤️"

async def get_json(url:str,params:dict[str,Any])->dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r=await client.get(url,params=params); r.raise_for_status(); return r.json()

async def weather_tool(location:str)->dict:
    geo=await get_json("https://geocoding-api.open-meteo.com/v1/search",{"name":location,"count":1,"language":"en","format":"json"})
    results=geo.get("results",[])
    if not results: raise HTTPException(404,f"Could not find the location '{location}'.")
    place=results[0]
    forecast=await get_json("https://api.open-meteo.com/v1/forecast",{
        "latitude":place["latitude"],"longitude":place["longitude"],
        "current":"temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
        "daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset",
        "timezone":"auto","forecast_days":5,"temperature_unit":"celsius","wind_speed_unit":"kmh"})
    c=forecast["current"]; d=forecast["daily"]
    days=[{"date":d["time"][i],"label":label(d["weather_code"][i]),"icon":icon(d["weather_code"][i]),"max":d["temperature_2m_max"][i],"min":d["temperature_2m_min"][i],"rain_probability":d["precipitation_probability_max"][i]} for i in range(5)]
    return {"location":{"name":place.get("name"),"admin1":place.get("admin1"),"country":place.get("country"),"latitude":place["latitude"],"longitude":place["longitude"],"timezone":forecast.get("timezone")},
            "current":{"temperature":c["temperature_2m"],"humidity":c["relative_humidity_2m"],"feels_like":c["apparent_temperature"],"precipitation":c["precipitation"],"condition":label(c["weather_code"]),"icon":icon(c["weather_code"],c.get("is_day",1)),"wind_speed":c["wind_speed_10m"],"wind_direction":c["wind_direction_10m"]},
            "sun":{"sunrise":d["sunrise"][0],"sunset":d["sunset"][0]},"forecast":days}

def fallback(data:dict)->dict:
    c=data["current"]; rain=data["forecast"][0]["rain_probability"]; t=c["temperature"]
    umbrella="Yes — rain is fairly likely today." if rain>=60 else ("Maybe — keep a compact umbrella nearby." if rain>=30 else "No — rain probability is low.")
    comfort="Light clothing and hydration are useful." if t>=32 else ("A light jacket would be useful." if t<=15 else "Conditions look reasonably comfortable.")
    return {"summary":f'{c["condition"]} with {t:.0f}°C, feeling like {c["feels_like"]:.0f}°C. Humidity is {c["humidity"]}% and wind is {c["wind_speed"]:.0f} km/h.',
            "advice":comfort,"umbrella":umbrella,"activity":"Outdoor plans look reasonable; keep an eye on the rain probability."}

async def ai_report(data:dict)->dict:
    fb=fallback(data)
    prompt=("You are a concise weather assistant. Use only this JSON weather data:\n"+
            json.dumps(data)+"\nReturn valid JSON with exactly these keys: summary, advice, umbrella, activity. "+
            "summary: 1-2 sentences. advice: clothing/comfort. umbrella: yes/no/maybe plus reason. "+
            "activity: practical outdoor recommendation. Do not invent facts. No markdown.")
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            r=await client.post(f"{OLLAMA_BASE_URL}/api/generate",json={"model":OLLAMA_MODEL,"prompt":prompt,"stream":False,"format":"json"})
            r.raise_for_status(); raw=r.json().get("response","")
            m=re.search(r"\{.*\}",raw,re.S)
            if not m:return fb
            x=json.loads(m.group(0))
            return {k:str(x.get(k,fb[k])) for k in fb}
    except Exception:return fb

@app.get("/")
async def home(): return FileResponse(BASE_DIR/"static"/"index.html")

@app.get("/api/health")
async def health(): return {"status":"ok","llm":"Ollama optional","model":OLLAMA_MODEL}

@app.get("/api/weather")
async def weather(location:str=Query(...,min_length=2,max_length=100)):
    data=await weather_tool(location.strip())
    return {"agent":{"name":"Weather AI Agent","tool":"Open-Meteo Weather Tool","llm":OLLAMA_MODEL},"weather":data,"ai":await ai_report(data)}
