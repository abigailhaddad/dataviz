<script>
    import JobBubbles from '$components/JobBubbles.svelte';
    import Scrolly from '$components/helpers/Scrolly.svelte';
    import { onMount } from 'svelte';
    import textContent from '$data/job-bubbles-text.json';
    import { isRedBubble } from '$utils/jobTitleClassification';
    
    let data = $state([]);
    let loading = $state(true);
    let error = $state(null);
    let scrollY = $state(0);
    let scrollIndex = $state(undefined);
    let highlightedNodes = $state([]);
    let currentHighlightIndex = $state(0);
    
    // Find the most popular title (largest bubble)
    let mostPopularTitle = $derived(
        data.length > 0 
            ? data.reduce((prev, current) => 
                (current.announcement_count > prev.announcement_count) ? current : prev
              ).job_title
            : ''
    );
    
    // Handle scroll step changes
    let intervalId;
    $effect(() => {
        if (scrollIndex !== undefined && data.length > 0) {
            const step = textContent.scrollSteps[scrollIndex];
            
            // Clear any existing interval
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
            
            switch(step.highlight) {
                case 'none':
                    highlightedNodes = [];
                    currentHighlightIndex = 0;
                    break;
                case 'mostPopular':
                    const mostPopular = data.find(d => d.job_title === mostPopularTitle);
                    highlightedNodes = mostPopular ? [mostPopular.job_title] : [];
                    currentHighlightIndex = 0;
                    break;
                case 'randomRed':
                    // Get several random red bubbles (IT Specialist variations)
                    const redBubbles = data.filter(d => isRedBubble(d.job_title));
                    const selectedRed = redBubbles
                        .sort(() => Math.random() - 0.5)
                        .slice(0, 5)
                        .map(d => d.job_title);
                    
                    // Cycle through them one at a time
                    if (selectedRed.length > 0) {
                        currentHighlightIndex = 0;
                        highlightedNodes = [selectedRed[0]];
                        
                        intervalId = setInterval(() => {
                            currentHighlightIndex = (currentHighlightIndex + 1) % selectedRed.length;
                            highlightedNodes = [selectedRed[currentHighlightIndex]];
                        }, 2000); // Change every 2 seconds
                    }
                    break;
                case 'randomGreen':
                    // Get several random green bubbles (other titles)
                    const greenBubbles = data.filter(d => !isRedBubble(d.job_title));
                    const selectedGreen = greenBubbles
                        .sort(() => Math.random() - 0.5)
                        .slice(0, 5)
                        .map(d => d.job_title);
                    
                    // Cycle through them one at a time
                    if (selectedGreen.length > 0) {
                        currentHighlightIndex = 0;
                        highlightedNodes = [selectedGreen[0]];
                        
                        intervalId = setInterval(() => {
                            currentHighlightIndex = (currentHighlightIndex + 1) % selectedGreen.length;
                            highlightedNodes = [selectedGreen[currentHighlightIndex]];
                        }, 2000); // Change every 2 seconds
                    }
                    break;
            }
        }
        
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    });
    
    onMount(async () => {
        try {
            // Load the processed JSON data
            const response = await fetch('/data/processed/job_titles_2024.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const allData = await response.json();
            
            // Show top 200 job titles by announcement count
            data = allData.slice(0, 200);
            console.log('Loaded', data.length, 'job titles');
            loading = false;
        } catch (err) {
            console.error('Error loading data:', err);
            error = err.message;
            loading = false;
        }
    });
</script>

<svelte:head>
    <title>{textContent.page.metaTitle}</title>
</svelte:head>

<svelte:window bind:scrollY />

<div class="container">
    <header>
        <h1>{textContent.page.title}</h1>
        <p class="subtitle">
            {@html textContent.page.subtitle}
        </p>
    </header>
    
    {#if error}
        <div class="error">Error loading data: {error}</div>
    {:else if loading}
        <div class="loading">Loading job data...</div>
    {:else if data.length > 0}
        <div class="scroll-container">
            <div class="visualization">
                <JobBubbles {data} height={700} {highlightedNodes} />
                <div class="legend">
                    <p class="legend-title">{textContent.legend.title}</p>
                    <div class="size-examples">
                        <div class="size-item">
                            <svg width="16" height="16">
                                <circle cx="8" cy="8" r="4" fill="#666" opacity="0.6"/>
                            </svg>
                            <span>{textContent.legend.sizeSmall}</span>
                        </div>
                        <div class="size-item">
                            <svg width="30" height="30">
                                <circle cx="15" cy="15" r="12" fill="#666" opacity="0.6"/>
                            </svg>
                            <span>{textContent.legend.sizeLarge}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="scroll-steps">
                <Scrolly bind:value={scrollIndex}>
                    {#each textContent.scrollSteps as step, i}
                        {@const active = scrollIndex === i}
                        {@const text = step.text.replace('{mostPopularTitle}', mostPopularTitle)}
                        <div class="step" class:active>
                            <div class="step-content">
                                <p>{@html text}</p>
                            </div>
                        </div>
                    {/each}
                </Scrolly>
            </div>
        </div>
    {:else}
        <div class="loading">No data found</div>
    {/if}
</div>

<footer>
    <div class="footer-content">
        <p class="footer-title">Find me online</p>
        <div class="footer-links">
            <a href="https://github.com/abigailhaddad" target="_blank" rel="noopener noreferrer">GitHub</a>
            <a href="https://abigailhaddad.netlify.app/" target="_blank" rel="noopener noreferrer">Website</a>
            <a href="https://presentofcoding.substack.com/" target="_blank" rel="noopener noreferrer">Blog</a>
        </div>
    </div>
</footer>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
        background-color: #192E3C;
        color: #f4f4f9;
        font-family: var(--serif);
    }
    
    .container {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }
    
    header {
        text-align: center;
        padding: 2rem 1rem;
        background: rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    h1 {
        margin: 0 0 1.5rem 0;
        font-size: 2.5rem;
        font-weight: 600;
        color: #fff;
        max-width: 600px;
        line-height: 1.2;
    }
    
    .subtitle {
        margin: 0;
        font-size: 1.125rem;
        opacity: 0.9;
        max-width: 600px;
        line-height: 1.5;
        padding: 0;
        text-align: left;
    }
    
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        
        .subtitle {
            font-size: 1rem;
        }
    }
    
    .visualization {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100vh;
        position: sticky;
        top: 0;
        padding-bottom: 40px;
        z-index: 1;
    }
    
    .loading {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        opacity: 0.7;
    }
    
    .error {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        color: #ff6b6b;
    }
    
    .legend {
        position: absolute;
        bottom: 0;
        text-align: center;
        background: rgba(25, 46, 60, 0.9);
        padding: 10px 20px;
        border-radius: 6px;
    }
    
    .legend-title {
        margin: 0 0 10px 0;
        font-family: var(--sans);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #fff;
        opacity: 0.8;
    }
    
    .size-examples {
        display: flex;
        gap: 20px;
        align-items: center;
        justify-content: center;
    }
    
    .size-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #fff;
        opacity: 0.7;
        font-family: var(--sans);
        font-size: 12px;
    }
    
    .scroll-container {
        position: relative;
    }
    
    .scroll-steps {
        position: relative;
        z-index: 2;
        padding: 100vh 0;
    }
    
    .step {
        min-height: 80vh;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        opacity: 0.3;
        transition: opacity 300ms ease;
        padding: 0 20px;
    }
    
    .step.active {
        opacity: 1;
    }
    
    .step-content {
        background: rgba(25, 46, 60, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 20px 25px;
        max-width: 400px;
        margin-left: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .step-content p {
        margin: 0;
        font-family: var(--sans);
        font-size: 16px;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.9);
    }
    
    @media (max-width: 768px) {
        .step-content {
            margin-left: 0;
            max-width: 90%;
        }
    }
    
    footer {
        background-color: rgba(0, 0, 0, 0.3);
        padding: 40px 20px;
        margin-top: 100px;
    }
    
    .footer-content {
        max-width: 600px;
        margin: 0 auto;
        text-align: center;
    }
    
    .footer-title {
        margin: 0 0 20px 0;
        font-family: var(--serif);
        font-size: 18px;
        color: rgba(255, 255, 255, 0.9);
        letter-spacing: 1px;
    }
    
    .footer-links {
        display: flex;
        gap: 30px;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .footer-links a {
        color: rgba(255, 255, 255, 0.7);
        text-decoration: none;
        font-family: var(--sans);
        font-size: 16px;
        transition: color 0.3s ease;
    }
    
    .footer-links a:hover {
        color: rgba(255, 255, 255, 1);
        text-decoration: underline;
    }
</style>