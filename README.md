# Federal Job Titles Visualization

This is a visualization of job titles in the federal government's 2210 (Information Technology Management) series, showing how generic titles like "IT Specialist" dominate the job postings on USAJobs.

## Running the Project

### Install dependencies
```bash
npm install
```

### Run development server
```bash
npm run dev
```

### Build for production
```bash
npm run build
```

The built files will be in the `build/` directory.

## Project Structure

### Data
- **Source data**: `/static/data/processed/job_titles_2024.json` - Contains the top 200 job titles by announcement count
- **Text content**: `/src/data/job-bubbles-text.json` - All UI text, titles, and scroll step content

### Key Components
- `/src/routes/+page.svelte` - Main visualization page with scrollytelling
- `/src/components/JobBubbles.svelte` - D3 force bubble chart component
- `/src/components/JobTooltip.svelte` - Tooltip for bubble hover/highlight
- `/src/components/helpers/Scrolly.svelte` - Scrollytelling component
- `/src/utils/jobTitleClassification.js` - Logic for categorizing job titles (red vs green)

## Credits

This project currently uses components from [The Pudding](https://pudding.cool/), especially their [Sleep Training visualization](https://pudding.cool/2024/07/sleep-training/).

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.