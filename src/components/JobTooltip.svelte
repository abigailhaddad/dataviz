<script>
    let { data, x, y, width } = $props();
    
    let tooltipX = $derived(x > width - 250 ? x - 220 : x + 20);
    let tooltipY = $derived(y > 300 ? y - 100 : y);
</script>

<div 
    class="tooltip" 
    style="left: {tooltipX}px; top: {tooltipY}px;"
>
    <h4>{data.job_title || 'Unknown Title'}</h4>
    <p>{data.announcement_count || 0} announcement{data.announcement_count !== 1 ? 's' : ''}</p>
</div>

<style>
    .tooltip {
        position: absolute;
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #1A2E3C;
        border-radius: 4px;
        padding: 12px;
        font-family: var(--sans, sans-serif);
        font-size: 14px;
        color: #1A2E3C;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        pointer-events: none;
        z-index: 1000;
        max-width: 300px;
    }
    
    h4 {
        margin: 0 0 4px 0;
        font-size: 16px;
        font-weight: 600;
        line-height: 1.2;
    }
    
    p {
        margin: 0;
        font-size: 13px;
        color: #666;
    }
</style>