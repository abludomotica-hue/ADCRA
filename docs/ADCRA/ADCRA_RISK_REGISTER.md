# ADCRA — MATRIZ Y REGISTRO DE RIESGOS v3.0
**Documento:** ADCRA_RISK_REGISTER.md  
**Fecha:** 21 de Septiembre, 2026  
**Sistema:** ADCRA (Autonomous Digital Campaign & Creative Production System)  

---

## 1. Registro de Riesgos Técnicos, Operacionales y Arquitectónicos

| ID | Categoría | Descripción del Riesgo | Impacto | Probabilidad | Nivel de Riesgo | Estrategia de Mitigación Implementada |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R-01** | **Hardware / GPU** | GPU NVIDIA GeForce GTX 750 Ti cuenta con 2GB VRAM (Maxwell Compute 5.0). Renders 4K o múltiples capas simultáneas en DaVinci Resolve podrían agotar la VRAM. | **ALTO** | **MEDIO** | **AMARILLO** | Limitar resolución de trabajo de preview a 720x1280 (vertical 9:16) y conformación de timeline optimizada. Utilizar fallback a FFmpeg para transcodificación si Resolve excede memoria. |
| **R-02** | **DaVinci Resolve GUI** | DaVinci Resolve en Linux puede requerir un servidor X11/display activo para inicializar ciertas funciones del Project Manager. | **MEDIO** | **MEDIO** | **AMARILLO** | Generar scripts independientes de importación (`import_to_resolve.py`, `setup_project.sh`) y EDL/XML estándar CMX 3600 y FCP7, permitiendo conformación headless o ejecución interactiva con un clic. |
| **R-03** | **Dependencias de Audio** | `librosa` no está instalada en el entorno global y requiere compiladores complejos de C/Fortran para `llvmlite` / `numba`. | **MEDIO** | **BAJO** | **VERDE** | Se utiliza `scipy.signal` y `soundfile`, que están completamente instaladas y calculan el tempo a 107.7 BPM con 100% de reproducibilidad sin latencia. |
| **R-04** | **Regresiones en Test Suite** | Modificaciones en los modelos de datos o rutas de API podrían romper las 270 pruebas existentes. | **CRÍTICO**| **BAJO** | **ROJO** | Principio de "Evolucionar antes que Reemplazar". Toda modificación debe ejecutar el comando de test suite completo (`python3 -m unittest discover tests -v`) antes de considerarse completa. |
| **R-05** | **Alucinación de la IA** | Presentar inferencias probabilísticas como si fuesen datos confirmados del cliente. | **ALTO** | **BAJO** | **AMARILLO** | Regla de Oro Epistemológica: Todo dato debe etiquetarse explícitamente con `source` (`CLIENT_INPUT`, `CONFIRMED_FACT`, `AI_INFERENCE`, `AI_RECOMMENDATION`, `UNKNOWN`) y `confidence`. |
| **R-06** | **Operaciones Destructivas** | Sobrescritura o eliminación accidental de material audiovisual original (`Recursos/videos/`, `Recursos/Audios/`). | **CRÍTICO**| **MUY BAJO**| **ROJO** | Los archivos fuente en `Recursos/` se tratan como de solo lectura. Todo procesamiento se vuelca en `campaign/` y `campaign/deliverables/`. |
| **R-07** | **Seguridad y Secretos** | Exposición de credenciales o claves API en manifiestos de campaña o logs. | **ALTO** | **MUY BAJO**| **AMARILLO** | Ningún secreto se guarda en JSONs de campaña, ni en el frontend. Autenticación desacoplada y validación de rutas contra path traversal. |
| **R-08** | **Desalineación de Safe Zones** | Textos o logotipos cubiertos por la interfaz nativa de TikTok, Reels o Shorts. | **ALTO** | **BAJO** | **AMARILLO** | Regla estricta de exclusión vertical (15% top / 20% bottom) validada automáticamente en Camera 3 de QC y en el visualizador de `Aesthetics Studio`. |
