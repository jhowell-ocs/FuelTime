# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in FuelTime, please report it by emailing jhowell@ocboe.com.

**Please do not report security vulnerabilities through public GitHub issues.**

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

### Response Timeline

- Initial response: Within 48 hours
- Status update: Within 1 week
- Fix deployment: Based on severity (Critical: 24-48 hours, High: 1 week, Medium: 2 weeks)

## Security Measures

### Current Implementations

1. **Input Validation**: Basic filename sanitization for file downloads
2. **Environment Isolation**: Separate temp directories for local vs container
3. **Dependency Management**: Regular updates and security scanning
4. **Docker Security**: Non-root user, minimal base image, regular updates

### Planned Improvements

1. **Enhanced Input Validation**: Comprehensive form data validation
2. **Security Headers**: CSRF protection, Content Security Policy
3. **Rate Limiting**: Protection against abuse
4. **Audit Logging**: Track all form submissions and PDF generations
5. **Secret Management**: Environment-based configuration

## Known Security Considerations

### Path Traversal Protection

The application uses regex validation to prevent directory traversal attacks in file downloads. File names are restricted to alphanumeric characters, spaces, hyphens, underscores, and periods.

### Temporary File Management

PDF files are temporarily stored in a dedicated directory. Consider implementing:
- Automatic cleanup of files older than 24 hours
- Per-user temporary directories
- Encrypted storage for sensitive data

### Debug Endpoints

Multiple debug endpoints exist in the application. These should be:
- Disabled in production environments
- Protected with authentication
- Removed from production builds

### Dependency Vulnerabilities

Regular dependency updates are critical. Run security scans with:
```bash
pip install safety
safety check
```

## Best Practices

### For Deployment

1. **Never expose debug endpoints** in production
2. **Use HTTPS only** with valid SSL certificates
3. **Implement authentication** for administrative functions
4. **Regular backups** of configuration and data
5. **Monitor logs** for suspicious activity
6. **Keep dependencies updated** monthly

### For Development

1. **Use virtual environments** to isolate dependencies
2. **Run security scans** before committing code
3. **Review code changes** for security implications
4. **Test with realistic data** but never use production data in development
5. **Document security considerations** for new features

## Security Contact

For security-related questions or concerns:
- Email: jhowell@ocboe.com
- Organization: Obion County Schools

## Acknowledgments

We appreciate the responsible disclosure of security vulnerabilities and will acknowledge contributors (with permission) in our security advisories.
