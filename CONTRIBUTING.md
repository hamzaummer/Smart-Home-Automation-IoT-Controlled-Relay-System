# Contributing to IoT Controlled Relay Project

Thank you for your interest in contributing to the IoT Controlled Relay project! We welcome contributions from the community and appreciate your help in making this project better.

## 🤝 How to Contribute

### Reporting Issues
Before creating a new issue, please:

1. Search existing issues to avoid duplicates  
2. Use the issue templates when available  
3. Provide clear, detailed information  
4. Include steps to reproduce for bug reports  
5. Specify your hardware setup and firmware version  

### Suggesting Features
We welcome new feature ideas! Please:

1. Check existing feature requests first  
2. Explain the use case and benefits  
3. Consider backward compatibility  
4. Be open to discussion and refinement  

### Code Contributions

#### Getting Started
1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/pico-w-relay-controller.git
   cd pico-w-relay-controller
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Development Environment**
   - Install [Thonny IDE](https://thonny.org/) or your preferred MicroPython editor  
   - Set up Raspberry Pi Pico W with MicroPython firmware  
   - Review the project structure and code organization  

#### Code Standards

**Code Style**
- Follow **PEP 8** Python style guidelines where applicable  
- Use meaningful variable and function names  
- Include **docstrings** for all classes and functions  
- Keep functions small and focused (**single responsibility**)  
- Use **type hints** where beneficial for clarity  

**Example Code Style:**
```python
def set_relay_state(self, state: bool, force: bool = False) -> bool:
    """
    Set relay state with safety checks.
    
    Args:
        state: Desired relay state (True=ON, False=OFF)
        force: Skip safety checks if True
        
    Returns:
        bool: True if successful, False otherwise
    """
    if self.relay_pin is None:
        self.logger.error("Relay not initialized")
        return False
    # Implementation here...
```
# Error Handling

- Use try-catch blocks for operations that may fail  
- Log errors appropriately with context  
- Provide graceful degradation where possible  
- Clean up resources in finally blocks  

# Memory Management

- Be mindful of memory usage in MicroPython  
- Use garbage collection where appropriate  
- Avoid memory leaks in long-running operations  
- Test with limited memory scenarios  

# Testing Requirements

## Hardware Testing
- Test on actual Raspberry Pi Pico W hardware  
- Verify with different relay modules (3.3V and 5V)  
- Test WiFi connectivity in various conditions  
- Validate safety features under stress conditions  

## Functional Testing
- Test all web interface features  
- Verify API endpoints work correctly  
- Test configuration loading and saving  
- Validate error handling scenarios  

## Performance Testing
- Monitor memory usage during extended operation  
- Test concurrent web requests  
- Verify system stability over time  
- Check response times for critical operations  

# Documentation

## Code Documentation
- Add inline comments for complex logic  
- Update docstrings for modified functions  
- Include examples for new features  
- Document any breaking changes  

## User Documentation
- Update README.md for new features  
- Add configuration examples  
- Include troubleshooting information  
- Update API documentation  

# Submission Process

## 1. Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature description"
```
## 2. Use Conventional Commits
- `feat:` – New features  
- `fix:` – Bug fixes  
- `docs:` – Documentation changes  
- `style:` – Code style changes  
- `refactor:` – Code refactoring  
- `test:` – Adding tests  
- `chore:` – Maintenance tasks  

## 3. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

## 4. Create Pull Request

## Steps to Create a Pull Request
- **Use the pull request template**
- **Provide a clear description** of changes
- **Reference related issues**
- **Include testing information**



## Pull Request Guidelines

### Before Submitting
- Code follows project style guidelines
- All tests pass on hardware
- Documentation is updated
- Commit messages are clear
- No unnecessary files included

### Pull Request Content
- **Clear title** summarizing the change
- **Detailed description** of what changed and why
- Links to related issues
- Screenshots for UI changes
- Test results and hardware compatibility

### Review Process
- Maintainers will review within **1–2 weeks**
- Address feedback promptly
- Be open to suggestions and changes
- Maintain professional, respectful communication

---

## 🏗️ Development Setup

### Required Tools
- **Hardware:** Raspberry Pi Pico W, relay module, breadboard
- **Software:** Thonny IDE or compatible MicroPython editor
- **Firmware:** MicroPython 1.19.1+ for Raspberry Pi Pico W

### Project Structure

├── main.py              # Application entry point

├── config.py            # Configuration management

├── wifi_manager.py      # WiFi connectivity

├── web_server.py        # HTTP server

├── relay_controller.py  # Relay control

├── logger.py           # Logging system

├── config.json         # Configuration file

└── docs/               # Documentation


### Development Workflow
1. Create a feature branch  
2. Make incremental commits  
3. Test thoroughly on hardware  
4. Update documentation  
5. Submit pull request  

---

## 🐛 Bug Reports

When reporting bugs, please include:
- **Hardware Setup:** Pico W model, relay module, power supply
- **Firmware Version:** MicroPython version and date
- **Steps to Reproduce:** Clear, numbered steps
- **Expected Behavior:** What should happen
- **Actual Behavior:** What actually happens
- **Logs:** Console output and error messages
- **Configuration:** Relevant `config.py` settings

---

## 💡 Feature Requests

When suggesting new features, consider:
- **Use Case:** Why is this feature needed?
- **Implementation:** How might it work?
- **Compatibility:** Impact on existing functionality
- **Resources:** Memory and processing requirements
- **Priority:** How important is this feature?

---

## 🛡️ Security

### Reporting Security Issues
- **Do NOT** create public issues for vulnerabilities
- Email security concerns privately to project maintainers
- Include detailed information about the vulnerability
- Allow time for assessment and fixes before disclosure

### Security Guidelines
- Follow secure coding practices
- Validate all user inputs
- Use appropriate error handling
- Avoid exposing sensitive information in logs
- Consider network security implications

---

## 📋 Code of Conduct

### Our Standards
- Be respectful and professional
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Prioritize community well-being

### Unacceptable Behavior
- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing private information
- Spam or off-topic content
- Disruptive or unprofessional conduct

---

## 🏷️ Release Process

### Version Numbers
- Follow **semantic versioning** (`MAJOR.MINOR.PATCH`)
- Update `CHANGELOG.md` with each release
- Tag releases with version numbers
- Create GitHub releases with release notes

### Release Criteria
- All tests pass
- Documentation is current
- No known critical bugs
- Backward compatibility maintained (for minor releases)

---

## 🙋‍♀️ Getting Help

### Questions?
- Check existing documentation first
- Search closed issues for similar questions
- Create a new issue with the `"question"` label
- Be specific about what you need help with

### Want to Help?
- Look for `"good first issue"` labels
- Help with documentation improvements
- Test new features and report feedback
- Review pull requests from other contributors

---

**Thank you for contributing to the IoT Controlled Relay project!**  
Your contributions help make this a better tool for the entire community. 🚀
