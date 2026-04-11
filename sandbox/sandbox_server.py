# /home/data-analytics-agent/sandbox/sandbox_server.py

from __future__ import annotations

import io
import json
import math
import time
import traceback
from contextlib import redirect_stdout
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Oracle Forge Sandbox", version="1.0.0")


class ExecuteRequest(BaseModel):
    code: str = Field(..., description="Python code to execute")
    context: dict[str, Any] = Field(default_factory=dict, description="Input data for execution")


class ExecuteResponse(BaseModel):
    result: Any
    trace: list[str]
    validation_status: str
    error_if_any: str | None
    execution_time_seconds: float
    stdout: str | None


def _safe_json(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Sandbox server is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/execute", response_model=ExecuteResponse)
def execute(req: ExecuteRequest) -> ExecuteResponse:
    start = time.time()
    trace: list[str] = []
    stdout_buffer = io.StringIO()

    safe_builtins = {
        "len": len,
        "range": range,
        "min": min,
        "max": max,
        "sum": sum,
        "sorted": sorted,
        "enumerate": enumerate,
        "zip": zip,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "abs": abs,
        "round": round,
        "print": print,
    }

    safe_globals = {
        "__builtins__": safe_builtins,
        "math": math,
        "json": json,
    }

    local_vars: dict[str, Any] = {
        "context": req.context,
        "result": None,
        "trace": trace,
    }

    trace.append("sandbox execution started")

    try:
        with redirect_stdout(stdout_buffer):
            exec(req.code, safe_globals, local_vars)

        result = _safe_json(local_vars.get("result"))
        trace.append("code executed successfully")

        return ExecuteResponse(
            result=result,
            trace=trace,
            validation_status="success",
            error_if_any=None,
            execution_time_seconds=round(time.time() - start, 6),
            stdout=stdout_buffer.getvalue() or None,
        )

    except Exception:
        trace.append("code execution failed")

        return ExecuteResponse(
            result=None,
            trace=trace,
            validation_status="failed",
            error_if_any=traceback.format_exc(),
            execution_time_seconds=round(time.time() - start, 6),
            stdout=stdout_buffer.getvalue() or None,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sandbox_server:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
    )
