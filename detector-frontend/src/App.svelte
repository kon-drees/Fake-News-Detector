<script>
  import { predict, highlight, factCheck } from './lib/api.js';

  // STATE VARIABLES
  let text = $state('');
  let error = $state('');
  let showModal = $state(false);

  let wantsHighlights = $state(true); 
  let showHighlights = $state(true); 

  let isAnalyzing = $state(false);
  let isFactChecking = $state(false);

  let predictRes = $state(null);
  let highlightRes = $state(null);
  let factCheckRes = $state(null);
  let predictionCategory = $state(null);
  let score = $state(null);

  async function factcheck(){
    error = '';
    if (text.length < 10) {
      error = 'Please input a text of minimum ten characters.';
      return;
    }

    factCheckRes = null;
    isFactChecking = true;

    try {
      factCheckRes = await factCheck(text);
    } catch (err) {
      error = 'Fact-checking failed: ' + err.message;
    } finally {
      isFactChecking = false;
    }
  }

  async function analyze() {
    error = '';
    if (text.length < 10) {
      error = 'Please input a text of minimum ten characters.';
      return;
    }

    predictRes = null;
    highlightRes = null;
    predictionCategory = null;
    score = null;

    showHighlights = wantsHighlights;
    isAnalyzing = true;

    const predictPromise = predict(text);
    const highlightPromise = showHighlights ? highlight(text) : null;

    try {
      predictRes = await predictPromise;
      if (typeof predictRes?.prediction_result.score !== 'number') {
        throw new Error('Invalid prediction response');
      }
      score = predictRes.prediction_result.score.toFixed(4);

      predictionCategory = capitalizeFirstLetter(predictRes.prediction_result.label)
      
    } catch (err) {
      error = 'Prediction failed: ' + err.message;
    }

    if (highlightPromise) {
      try {
        highlightRes = await highlightPromise;
      } catch (err) {
        error = (error ? error + ' | ' : '') + 'Highlighting failed: ' + err.message;
      }
    }
    isAnalyzing = false;
  }

  function autoResize(element) {
    const el = element.target;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }

  function valueToBackground(value) {
    if (!value) return 'transparent';
    const intensity = Math.min(Math.abs(value), 1);
    return value > 0 
      ? `rgba(210, 0, 0, ${intensity})` 
      : `rgba(0, 210, 0, ${intensity})`;
  }

  function capitalizeFirstLetter(val) {
    return String(val).charAt(0).toUpperCase() + String(val).slice(1);
  }

  function getScoreColor(score) {
    if (score < 0.3) return '#4caf50'; // Green
    if (score < 0.7) return '#ff9800'; // Orange
    return '#ff5555'; // Red
  }
</script>

<main id="app-container">
  <header class="top-header">
    <h1 class="title">Fake News Detector</h1>
    <button class="info-btn" onclick={() => showModal = true} aria-label="Information">
      <i>i</i>
    </button>
  </header>

  <section id="input-section">
    <textarea id="text-input" class="input-box" oninput={autoResize} bind:value={text} placeholder="Paste a text or link here..."></textarea>
    
    <div class="controls">
      <button id="factcheck-button" class="btn" onclick={factcheck} disabled={isFactChecking}>
        {#if isFactChecking}
          <span class="spinner"></span>
          <span>Fact-Checking...</span>
        {:else}
          Fact-Check
        {/if}
      </button>

      <div class="row-group">
        <button id="analyze-button" class="btn" onclick={analyze} disabled={isAnalyzing}>
          {#if isAnalyzing}
            <span class="spinner"></span>
            <span>Analyzing...</span>
          {:else}
            Analyze
          {/if}
        </button>

        <label class="checkbox-label">
          <input type="checkbox" bind:checked={wantsHighlights} />
          Enable Highlighting
        </label>
      </div>
    </div>

    {#if error}
      <p class="error">{error}</p>
    {/if}
  </section>

  <hr class="divider"/>

  <section id="result-section">
    {#if factCheckRes !== null}
      <div id="fact-checking-values" class="result-card">
        <h2>Fact-Checking Result</h2>
        
        <div class="score-container">
          <span class="score-label">Fake Probability Score:</span>
          <span class="score-value" style="color: {getScoreColor(factCheckRes.fake_score)}">
            {(factCheckRes.fake_score * 100).toFixed(1)}%
          </span>
        </div>

        <hr class="divider-small"/>

        <div class="analysis-box">
           <h3>Analysis Summary</h3>
           <p>{factCheckRes.summary_analysis}</p>
        </div>

        {#if factCheckRes.checked_claims && factCheckRes.checked_claims.length > 0}
          <div class="claims-list">
            <h3>Verified Claims</h3>
            {#each factCheckRes.checked_claims as claim}
              <div class="claim-card">
                <p><strong>Claim:</strong> {claim.claim}</p>
                <p><strong>Result:</strong> {claim.assessment}</p>
                <p><strong>Reasoning:</strong> {claim.reasoning}</p>
              </div>
            {/each}
          </div>
        {/if}

      </div>
    {/if}

    {#if predictRes !== null}
      <div id="prediction-values" class="result-card">
        <h2>Prediction Result</h2>
        <p><strong>Prediction:</strong> {predictionCategory}</p>
        <p><strong>Confidence Score:</strong> {(score * 100).toFixed(2)}%</p>
      </div>
    {/if}

    {#if highlightRes && showHighlights}
      <div id="highlighted-text" class="result-card">
        <h3>Prediction Reasoning</h3>
        <p class="highlight-legend">
          <span class="legend-green">Green</span> → Low fake news probability.<br>
          <span class="legend-red">Red</span> → High fake news probability.
        </p>
        <hr class="divider" />
        <p class="highlighted-words">
          {#each highlightRes.highlights as token}
            <span class="highlight-word" style="background-color: {valueToBackground(token.score_normalized)}">
              {token.token}
            </span>
          {/each}
        </p>
      </div>
    {/if}
  </section>

  {#if showModal}
    <div class="modal-overlay" onclick={() => showModal = false} role="presentation">
      <div class="modal-content" onclick={(e) => e.stopPropagation()} role="dialog">
        <button class="close-btn" onclick={() => showModal = false}>&times;</button>
        <h2>Instructions & Documentation</h2>
        <p>This tool uses machine learning to analyze the probability of a text being "Fake News".</p>
        <ul>
          <li><strong>Analyze:</strong> Sends your text to the model for scoring.</li>
          <li><strong>Highlighting:</strong> When enabled, specific words are color-coded based on their influence on the score. This may take a while for longer input texts.</li>
          <li><strong>Privacy:</strong> Your text is processed for analysis but not stored.</li>
        </ul>
        <p>Minimum input length is 10 characters. Links to news article websites are also accepted.</p>
      </div>
    </div>
  {/if}
</main>