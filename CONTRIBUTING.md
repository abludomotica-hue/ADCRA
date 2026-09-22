# Contributing to ADCRA

Thank you for your interest in contributing to **ADCRA** (*Autonomous Digital Campaign & Creative Production System*)! We welcome contributions from software engineers, creative technologists, video editors, AI researchers, and agency workflow experts.

---

## Code of Conduct

We are committed to providing a welcoming, diverse, and harassment-free environment for everyone. Please treat all contributors with respect and professionalism.

---

## Development Workflow

### 1. Prerequisites
- **Python**: 3.10, 3.11, 3.12, or 3.13
- **Node.js**: v18.0+ / v20.0+ / v22.0+
- **FFmpeg**: v6.0+ or v7.0+ (`ffmpeg`, `ffprobe` in `$PATH`)
- **Git**

### 2. Fork & Setup
```bash
# 1. Clone your fork
git clone https://github.com/<your-username>/ADCRA.git
cd ADCRA

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install core and dev dependencies
pip install -r requirements-dev.txt

# 4. Copy environment variables
cp .env.example .env
```

### 3. Running the Test Suite
All contributions must pass the complete regression test suite without failures:
```bash
# Run all unit and integration tests
python3 -m unittest discover -s tests -q

# Or use the ADCRA CLI helper
python3 adcra_cli.py test
```

### 4. Code Standards
- **Python**: PEP 8 compliance. Type hints (`typing`) are strongly encouraged for all public functions and agent interfaces.
- **Security**: Never commit raw API keys or hardcoded tokens. Use environment variables.
- **Path Sanitization**: Any HTTP endpoint serving artifacts must sanitize file paths against directory traversal (`../`).
- **Verbal Economy**: When adding agent prompts or routing behaviors, enforce token limits and avoid unnecessary verbosity.

---

## How to Add New Features

### Adding a New AI Agent Profile
1. Navigate to `adcra/ai/profiles.py`.
2. Define the agent's role, system instructions, temperature, default tool permissions, and model tier.
3. Add a unit test in `tests/test_ai_brain_routing.py` or create a new test file.

### Adding a New Tool / Creative Skill
1. Define the tool function in `adcra/ai/tools.py`.
2. Add the JSON Schema definition for arguments and output.
3. Register the tool in `get_default_tool_registry()` with proper role-based permissions (`adcra/ai/permissions.py`).
4. Add unit tests verifying schema validation and execution safety.

### Extending the Web UI
1. Inspect `dashboard_server.py` and `web/` assets.
2. Ensure new UI components work seamlessly across responsive viewports and dark-mode themes.

---

## Submitting Pull Requests

1. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-creative-feature
   ```
2. Commit your changes with clear, semantic commit messages:
   ```bash
   git commit -m "feat(ai-brain): add Claude 3.7 Sonnet reasoning tier"
   ```
3. Push to your branch and open a Pull Request against the `main` branch.
4. Describe your changes clearly in the PR description, including test coverage details.

---

## License

By contributing to ADCRA, you agree that your contributions will be licensed under the [Apache 2.0 License](LICENSE).
