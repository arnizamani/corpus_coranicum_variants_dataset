# Contributing to Corpus Coranicum Variants Dataset

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Ways to Contribute

### 1. Report Issues

If you find any problems with the data or code:

- Check if the issue already exists in the [Issues](https://github.com/arnizamani/corpus_coranicum_variants_dataset/issues) section
- If not, create a new issue with:
  - Clear title and description
  - Steps to reproduce (if applicable)
  - Expected vs actual behavior
  - Relevant verse references (surah:verse)

### 2. Improve Documentation

- Fix typos or unclear explanations
- Add examples or use cases
- Improve transliteration documentation
- Translate documentation to other languages

### 3. Add Features

Potential contributions:
- Additional data validation tests
- Conversion to other formats (SQL, Parquet, RDF, etc.)
- Analysis tools and visualizations
- API or web interface
- Integration with other Quranic datasets

### 4. Fix Bugs

- Check the Issues section for bugs
- Submit a pull request with the fix
- Include tests if applicable

## Development Setup

### Prerequisites

```bash
# Node.js (for scraping)
node --version  # Should be >= 14.0.0

# Python (for data processing)
python3 --version  # Should be >= 3.7
```

### Installation

```bash
# Clone the repository
git clone https://github.com/arnizamani/corpus_coranicum_variants_dataset.git
cd corpus_coranicum_variants_dataset

# Install Node.js dependencies
npm install

# Install Python dependencies
uv sync
```

### Running Tests

```bash
# Run all validation tests
uv run pytest test_variants.py -v

# Run specific test
uv run pytest test_variants.py::TestVariantsStructure::test_ayah_count -v
```

## Pull Request Process

1. **Fork the repository** and create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   uv run pytest test_variants.py -v
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Provide a clear description of changes

## Code Style

### Python

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

Example:
```python
def get_variants_for_verse(data, surah, verse):
    """Get all variants for a specific verse.
    
    Args:
        data: List of verse dictionaries
        surah: Surah number (1-114)
        verse: Verse number
        
    Returns:
        Dictionary with verse data or None if not found
    """
    return next((v for v in data if v['surah'] == surah and v['verse'] == verse), None)
```

### JavaScript

- Use const/let instead of var
- Use async/await for asynchronous code
- Add comments for complex logic

Example:
```javascript
async function scrapeVariants(surah, verse) {
  // Launch browser and navigate to page
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Scrape data...
    return { surah, verse, variants: data, success: true };
  } catch (error) {
    return { surah, verse, error: error.message, success: false };
  } finally {
    await browser.close();
  }
}
```

## Data Quality Guidelines

When working with the data:

1. **Preserve source attribution**: Always maintain the `work` field
2. **Validate changes**: Run tests after modifications
3. **Document special cases**: Add comments for unusual handling
4. **Maintain consistency**: Follow existing patterns

## Testing Guidelines

### Adding New Tests

```python
def test_new_feature(self):
    """Test description."""
    # Arrange
    data = load_test_data()
    
    # Act
    result = your_function(data)
    
    # Assert
    self.assertEqual(result, expected_value)
```

### Test Coverage

Aim to test:
- Normal cases
- Edge cases (empty data, missing fields)
- Error conditions
- Data integrity

## Documentation Guidelines

- Use clear, concise language
- Provide examples for complex concepts
- Include code snippets where helpful
- Keep README.md focused on getting started
- Put detailed information in DATA.md

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
Add validation test for word positions

- Checks that all word positions are positive integers
- Verifies no gaps in complete readings
- Fixes issue #123
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description (if needed)
- Reference issues with #number

## Questions?

If you have questions about contributing:

1. Check existing documentation (README.md, DATA.md)
2. Search closed issues for similar questions
3. Open a new issue with the "question" label

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Respect different perspectives

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT for code, CC BY-SA 4.0 for data).

---

Thank you for contributing to this project! Your efforts help make Quranic scholarship more accessible to everyone.
