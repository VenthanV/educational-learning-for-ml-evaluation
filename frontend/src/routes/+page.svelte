<script>
    import { onMount } from 'svelte';

    let scenarios = $state(null); // Speichert alle Szenarien vom Backend
    let selectedScenarioId = $state(null); // Welches Level wurde geklickt?


    let threshold = $state(0.5);
    let metricsData = $state(null);
    let loadingMetrics = $state(false);

    onMount(async () => {
        try {
            const res = await fetch('http://localhost:8000/api/scenarios');
            scenarios = await res.json();
        } catch (error) {
            console.error("Fehler beim Laden der Szenarien:", error);
        }
    });


    $effect(() => {
        if (selectedScenarioId !== null) {
            fetchMetrics(selectedScenarioId, threshold);
        }
    });

    async function fetchMetrics(scenario_id, current_threshold) {
        loadingMetrics = true;
        try {
            const response = await fetch('http://localhost:8000/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    scenario_id: scenario_id,
                    threshold: current_threshold
                })
            });
            metricsData = await response.json();
        } catch (error) {
            console.error("Fehler bei der Evaluierung:", error);
        } finally {
            loadingMetrics = false;
        }
    }

    function goBack() {
        selectedScenarioId = null;
        metricsData = null;
        threshold = 0.5; // Slider zurücksetzen
    }
</script>

<style>
    :global(body) { margin: 0; font-family: system-ui, sans-serif; background-color: #f8fafc; color: #0f172a; }

    .hero { text-align: center; padding: 4rem 2rem; background: #1e293b; color: white; }
    .hero h1 { font-size: 3rem; margin: 0; color: #38bdf8; }
    .hero p { font-size: 1.2rem; color: #cbd5e1; max-width: 600px; margin: 1rem auto; }

    .grid-container { max-width: 1200px; margin: -2rem auto 2rem; padding: 0 2rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; }

    .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; border: 1px solid #e2e8f0; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1); border-color: #38bdf8; }
    .card h3 { margin-top: 0; color: #0f172a; font-size: 1.4rem; }
    .card p { color: #64748b; line-height: 1.5; }
    .start-btn { display: inline-block; margin-top: 1rem; background: #38bdf8; color: #0f172a; font-weight: bold; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; }

    .lab-container { display: flex; height: 100vh; }
    .sidebar { width: 35%; background: #1e293b; color: white; padding: 2rem; overflow-y: auto; }
    .sidebar h2 { color: #38bdf8; }
    .back-btn { background: transparent; border: 1px solid #64748b; color: #cbd5e1; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; margin-bottom: 2rem; transition: background 0.2s; }
    .back-btn:hover { background: #334155; color: white; }

    .lab-main { width: 65%; padding: 2rem; display: flex; flex-direction: column; gap: 2rem; overflow-y: auto; }
    .control-panel { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .slider { width: 100%; cursor: pointer; margin-top: 1rem; }

    .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #e2e8f0; }
    .metric-value { font-size: 2.5rem; font-weight: bold; color: #0f172a; margin-top: 0.5rem; }
    .metric-label { font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: bold; }
</style>

{#if selectedScenarioId === null}

    <div class="hero">
        <h1>Cyber ML Evaluator</h1>
        <p>Lerne spielerisch die Schwächen von Machine Learning Metriken kennen. Wähle ein Szenario aus.</p>
    </div>

    {#if !scenarios}
        <div style="text-align: center; margin-top: 4rem; color: #64748b;">Verbinde mit Server...</div>
    {:else}
        <!-- Grid der Level-Kacheln -->
        <div class="grid-container">
            {#each Object.entries(scenarios) as [id, data]}
                <!-- Wenn man auf die Karte klickt, wird die ID gesetzt und das Labor öffnet sich -->
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div class="card" onclick={() => selectedScenarioId = id}>
                    <h3>{data.title}</h3>
                    <p>{data.description}</p>
                    <div class="start-btn">Labor öffnen &rarr;</div>
                </div>
            {/each}
        </div>
    {/if}

{:else}

    <div class="lab-container">
        <!-- Linke Spalte: Guide -->
        <div class="sidebar">
            <button class="back-btn" onclick={goBack}>&larr; Zurück zur Übersicht</button>

            <!-- Wir holen Titel und Beschreibung direkt aus dem geladenen Szenario -->
            <h2>{scenarios[selectedScenarioId].title}</h2>
            <div style="background: #334155; padding: 1.5rem; border-radius: 8px; line-height: 1.6;">
                <p>{scenarios[selectedScenarioId].description}</p>
                <hr style="border-color: #475569; margin: 1.5rem 0;" />
                <p><strong>Deine Aufgabe:</strong> Justiere den Schwellenwert rechts und beobachte, wie das Modell reagiert. Wann bricht die Precision ein? Wann fällt der Recall?</p>
            </div>
        </div>

        <!-- Rechte Spalte: Labor -->
        <div class="lab-main">
            <div class="control-panel">
                <h3 style="margin-top: 0;">Entscheidungsgrenze (Threshold): {threshold.toFixed(2)}</h3>
                <p style="color: #64748b; margin-bottom: 1.5rem;">Wahrscheinlichkeiten ab {threshold.toFixed(2)} werden als Angriff gewertet.</p>
                <input
                    type="range"
                    class="slider"
                    min="0" max="1" step="0.05"
                    bind:value={threshold}
                />
            </div>

            <!-- Metriken aus dem Python Backend -->
            {#if metricsData}
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Accuracy</div>
                        <div class="metric-value" style="color: {metricsData.metrics.accuracy > 0.9 ? '#10b981' : '#0f172a'};">{metricsData.metrics.accuracy}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Precision</div>
                        <div class="metric-value">{metricsData.metrics.precision}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Recall</div>
                        <div class="metric-value">{metricsData.metrics.recall}</div>
                    </div>
                    <div class="metric-card" style="background: #f0f9ff; border-color: #bae6fd;">
                        <div class="metric-label" style="color: #0284c7;">F1-Score</div>
                        <div class="metric-value" style="color: #0369a1;">{metricsData.metrics.f1_score}</div>
                    </div>
                </div>
            {:else if loadingMetrics}
                <p>Berechne Metriken...</p>
            {/if}
        </div>
    </div>

{/if}