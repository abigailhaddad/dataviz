<script>
    import { forceSimulation, forceY, forceX, forceCollide } from 'd3-force';
    import { scaleSqrt } from 'd3-scale';
    import { fade } from "svelte/transition";
    import { onMount } from 'svelte';
    
    import Tooltip from "$components/JobTooltip.svelte";
    import { getJobTitleColor } from "$utils/jobTitleClassification";

    let { data = [], height = 800, highlightedNodes = [] } = $props();
    
    let viewportWidth = $state(0);
    let width = $derived(viewportWidth * 0.9);
    let nodes = $state([]);
    let hoveredNode = $state(null);
    let mounted = false;

    const margin = { top: 50, right: 50, bottom: 50, left: 50 };
    let innerWidth = $derived(width - margin.right - margin.left);
    let innerHeight = $derived(height - margin.top - margin.bottom);

    // Use shared color function
    const getNodeColor = (node) => {
        return getJobTitleColor(node.job_title);
    };

    // Scale for bubble radius based on number of announcements
    let radiusScale = $derived(
        scaleSqrt()
            .domain([0, Math.max(...data.map(d => d.announcement_count || 1))])
            .range([3, 40])
    );

    $effect(() => {
        if (data && data.length > 0) {
            rerunSimulation();
        }
    });

    function rerunSimulation(){
        if(mounted && data.length > 0){
            let dataToSimulate = data.map(d => ({
                ...d,
                radius: radiusScale(d.announcement_count || 1),
                isRed: getNodeColor(d) === '#A34131' // Check if it should be red (generic titles)
            }));

            let simulation = forceSimulation(dataToSimulate)
                .on("tick", () => {
                    nodes = simulation.nodes();
                });

            simulation.nodes(dataToSimulate)
                .force("x", forceX(d => {
                    // Separate red (left) and green (right) but closer together
                    return d.isRed ? innerWidth * 0.35 : innerWidth * 0.65;
                }).strength(1))  // Much stronger force
                .force("y", forceY(innerHeight / 2).strength(1))  // Much stronger force
                .force("collide", forceCollide()
                    .radius(d => d.radius + 1)
                    .strength(1)
                );

            // Faster settling with more aggressive alpha decay
            simulation.alpha(1).alphaDecay(0.05).velocityDecay(0.4).restart();
        }
    }

    onMount(() => {
        mounted = true;
        rerunSimulation();
    });
</script>

<svelte:window bind:innerWidth={viewportWidth} />

<div class="chart-container">
    <svg {width} {height} onmouseleave={() => (hoveredNode = null)} role="img" aria-label="Job titles bubble chart">
        <g class="inner-bubbles" transform="translate({margin.left}, {margin.top})">
            {#each nodes as node, index}
                <circle
                    cx={node.x}
                    cy={node.y}
                    r={node.radius}
                    fill={getNodeColor(node)}
                    opacity={hoveredNode
                        ? hoveredNode === node
                            ? 1
                            : 0.3
                        : highlightedNodes.length > 0
                            ? highlightedNodes.includes(node.job_title)
                                ? 1
                                : 0.3
                            : 0.8}
                    stroke="#1A2E3C"
                    stroke-width="2"
                    onmouseover={() => (hoveredNode = node)}
                    onfocus={() => (hoveredNode = node)}
                    onmouseleave={() => (hoveredNode = null)}
                    in:fade={{ duration: 200 }}
                    style="cursor: pointer; transition: opacity 300ms ease, cx 100ms ease, cy 100ms ease;"
                    role="button"
                    tabindex="0"
                    aria-label="{node.job_title}: {node.announcement_count} announcements"
                />
            {/each}
            
            <!-- Group labels with background -->
            <g transform="translate({innerWidth * 0.35}, {innerHeight * 0.5})" style="pointer-events: none;">
                <rect x="-90" y="-15" width="180" height="30" fill="#192E3C" opacity="0.8" rx="4"/>
                <text text-anchor="middle" class="group-label">
                    IT Specialist
                </text>
            </g>
            <g transform="translate({innerWidth * 0.65}, {innerHeight * 0.5})" style="pointer-events: none;">
                <rect x="-70" y="-15" width="140" height="30" fill="#192E3C" opacity="0.8" rx="4"/>
                <text text-anchor="middle" class="group-label">
                    Other Titles
                </text>
            </g>
        </g>
    </svg>
    
    {#if hoveredNode}
        <Tooltip data={hoveredNode} x={hoveredNode.x + margin.left} y={hoveredNode.y + margin.top} {width} />
    {:else if highlightedNodes.length === 1}
        {@const highlightedNode = nodes.find(n => n.job_title === highlightedNodes[0])}
        {#if highlightedNode}
            <Tooltip data={highlightedNode} x={highlightedNode.x + margin.left} y={highlightedNode.y + margin.top} {width} />
        {/if}
    {/if}
</div>

<style>
    .chart-container {
        background-color: var(--custom-bg, #192E3C);
        width: 100%;
        height: 100%;
        position: relative;
    }
    
    svg {
        overflow: visible;
    }
    
    .group-label {
        font-family: var(--serif, serif);
        font-size: 16px;
        font-weight: 400;
        fill: #fff;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
</style>