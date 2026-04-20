# Contributing to CertainLogic Verifier

We welcome contributions! This project is built for transparency and trust, and we appreciate help from the community.

## How to Contribute

### 1. Reporting Issues
- Check if the issue already exists in the [Issues](https://github.com/CertainLogicAI/hallucination-guard/issues) tab
- Provide a clear description, steps to reproduce, and relevant logs/screenshots
- Include environment details (OS, Python version, etc.)

### 2. Suggesting Features
- Open an issue with the `enhancement` label
- Describe the use case, expected behavior, and why it would be valuable
- If possible, link to existing implementations or research

### 3. Submitting Pull Requests
1. **Fork** the repository
2. **Create a branch** for your feature/fix: `git checkout -b feature/your-feature-name`
3. **Make your changes** with clear commit messages
4. **Add tests** if applicable (unit tests for new validation rules, integration tests for API endpoints)
5. **Update documentation** (README, inline docstrings) as needed
6. **Run the existing tests** to ensure nothing breaks:
   ```bash
   python -m pytest tests/  # if we have a test suite
   ```
7. **Push** to your fork and open a Pull Request

### 4. Code Style
- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code
- Use type hints where helpful
- Write descriptive docstrings for public functions/classes
- Keep functions focused and modular

### 5. Areas That Need Help
- **Validation rule improvements** – better factual matching, contradiction detection, uncertainty patterns
- **Performance optimizations** – faster semantic caching, reduced memory footprint
- **Integration examples** – with LangChain, LlamaIndex, Haystack, etc.
- **Documentation** – more examples, tutorials, troubleshooting guides
- **Testing** – expand test coverage, add benchmark suites

### 6. Security Considerations
- **Do not** introduce external API calls without explicit opt‑in configuration
- **Do not** change the deterministic nature of verification without discussion
- **Do** flag any security concerns via security advisories, not public issues

## Community
- **Discussions**: Use GitHub Discussions for questions and brainstorming
- **X/Twitter**: Follow [@CertainLogicAI](https://x.com/CertainLogicAI) for updates
- **Email**: For sensitive security issues, contact security@certainlogic.ai

## License
By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

Thank you for helping make AI more reliable and transparent!