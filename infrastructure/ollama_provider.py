"""
Proveedor de modelos basado en Ollama.

Permite a SIGNA Core utilizar un modelo local en Ollama sin
depender directamente de la implementación del Core.
"""

import json
import time

import requests

from domain.enums import ModelStatus, Provider
from domain.schemas import (
    Classification, Incident, ModelMetrics, ModelResult,
)

class OllamaProvider:
    """Proveedor de modelos locales mediante Ollama."""

    def __init__(
        self,
        model: str = "llama3.2:3b",
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url

    def analyze(self, incident: Incident) -> ModelResult:
        """Analiza una incidencia utilizando Ollama"""
        start_time = time.perf_counter()

        prompt = f"""
Analiza la siguiente incidencia de telecomunicaciones.

Incidencia:
{incident.text}

Devuelve EXCLUSIVAMENTE un objeto JSON válido con esta estructura:
{{
    "category": "connectivity",
    "urgency": "medium",
    "department": "technical_support",
    "summary": "Exactamente diez palabras en español"
    "explanation": "Explicación breve de la clasificación"
    "confidence": 0.0
}}

valores permitidos para category:
technical_visit, mobile_network, installation, connectivity,
tv_service, contract, hardware, account, billing, other

Valores permitidos para urgency:
low, medium, high, critical

Valores permitidos para department:
technical_support, customer_service, field_service,
security, billing, sales

La propiedad confidence debe ser un número entro 0.0 y 1.0.
El summary debe contener exactamente 10 palabras.
No añadas markdown ni texto fuera del JSON.
"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout = 60,
            )

            response.raise_for_status()

            data = response.json()
            raw_result = data.get("response")

            if not raw_result:
                raise ValueError(
                    "Ollama returned an empty response"
                )

            parsed_result = json.loads(raw_result)

            classification = Classification(
                category = parsed_result["category"],
                urgency = parsed_result["urgency"],
                department = parsed_result["department"],
                summary = parsed_result["summary"],
                explanation = parsed_result["explanation"],
                confidence = parsed_result["confidence"], 
            )

            latency_ms = (
                time.perf_counter() - start_time
            ) * 1000

            input_tokens = data.get("prompt_eval_count", 0) 
            output_tokens = data.get("eval_count", 0) 

            metrics = ModelMetrics( 
                input_tokens=input_tokens, 
                output_tokens=output_tokens, 
                total_tokens=input_tokens + output_tokens, 
                latency_ms=latency_ms, cost=0.0, retries=0, 
            ) 

            return ModelResult( 
                provider=Provider.LOCAL, 
                model=self.model, 
                classification=classification, 
                metrics=metrics, 
                status=ModelStatus.SUCCESS, 
                error=None, 
            ) 

        except Exception as exc: 
            latency_ms = ( 
                time.perf_counter() - start_time 
            ) * 1000 

            metrics = ModelMetrics( 
                input_tokens=0, 
                output_tokens=0, 
                total_tokens=0, 
                latency_ms=latency_ms, 
                cost=0.0, 
                retries=0, 
            ) 

            return ModelResult( 
                provider=Provider.LOCAL, 
                model=self.model, 
                classification=None, 
                metrics=metrics, 
                status=ModelStatus.ERROR, 
                error=str(exc), 
            )