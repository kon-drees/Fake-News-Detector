<script>
  import { predict, highlight, factCheck } from './lib/api.js';
  import { 
    capitalizeFirstLetter, 
    getScoreColor, 
    valueToBackground, 
    autoResize 
  } from './lib/utils.js';

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

  let textOfLastRequest = '';

  function validateInput() {
    if (text.length < 10) {
      error = 'Please input a text of minimum ten characters.';
      return false;
    }
    return true;
  }

  async function factcheck() {
    error = '';
    if (!validateInput()) return;

    if (text !== textOfLastRequest) {
      predictRes = null;
    }

    factCheckRes = null;
    isFactChecking = true;

    try {
      factCheckRes = await factCheck(text);
    } catch (err) {
      error = 'Fact-checking failed: ' + err.message;
    } finally {
      isFactChecking = false;
      textOfLastRequest = text;
    }
  }

  async function analyze() {
    error = '';
    if (!validateInput()) return;

    if (text !== textOfLastRequest) {
      factCheckRes = null;
    }

    // Reset Analysis State
    predictRes = null;
    highlightRes = null;
    showHighlights = wantsHighlights;
    isAnalyzing = true;

    try {
      // Run prediction
      const pRes = await predict(text);
      if (typeof pRes?.prediction_result.score !== 'number') {
        throw new Error('Invalid prediction response');
      }
      predictRes = pRes;

      // Run highlight if requested
      if (showHighlights) {
        try {
          highlightRes = await highlight(text);
        } catch (hErr) {
          console.warn('Highlighting failed', hErr);
        }
      }
    } catch (err) {
      error = 'Prediction failed: ' + err.message;
    } finally {
      isAnalyzing = false;
      textOfLastRequest = text;
    }
  }
</script>

<main id="app-container">
  <header class="top-header">
    <div class="branding">
      <img id="logoicon" src="fake-news-detector-icon.png" alt="logo">
      <h1 class="title">Fake News Detector</h1>
    </div>
    <button class="info-btn" onclick={() => showModal = true} aria-label="Information">
      <i>i</i>
    </button>
  </header>

  <div id="description-div">
    The fake news detector uses an ai-agent for checking the actuallity of the provided content.
    Analyzing utilizes a LLM to determine if the provided input is fake-news.
    Highlighting shows what parts of the text were part of the reasoning for the resulting classification.
  </div>

  <section id="input-section">
    <textarea 
      id="text-input" 
      class="input-box" 
      spellcheck="false" 
      oninput={autoResize} 
      bind:value={text} 
      placeholder="Paste a text or link here...">
    </textarea>
    
    <div class="controls">
      <button id="factcheck-button" class="btn" onclick={factcheck} disabled={isFactChecking}>
        {#if isFactChecking}
          <span class="spinner"></span><span>Fact-Checking...</span>
        {:else}
          Fact-Check
        {/if}
      </button>

      <div class="row-group">
        <button id="analyze-button" class="btn" onclick={analyze} disabled={isAnalyzing}>
          {#if isAnalyzing}
            <span class="spinner"></span><span>Analyzing...</span>
          {:else}
            Analyze
          {/if}
        </button>

        <label class="checkbox-label">
          <input id="highlight-checkbox" type="checkbox" bind:checked={wantsHighlights} />
          Enable Highlighting
        </label>
      </div>
    </div>
  </section>

  <section>
    {#if error} <p class="error">{error}</p> {/if}
  </section>

  <hr class="divider"/>

  <section id="result-section">
    {#if factCheckRes !== null}
      <div id="fact-checking-values" class="result-card">
        <button class="tile-close-btn" onclick={() => factCheckRes = null} aria-label="Close">&times;</button>
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
        {#if factCheckRes.checked_claims?.length > 0}
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
        <button class="tile-close-btn" onclick={() => predictRes = null} aria-label="Close">&times;</button>
        <h2>Prediction Result</h2>
        <hr class="divider" />
        <p><strong>Prediction:</strong> {predictionCategory}</p>
        <p><strong>Confidence Score:</strong> {(score * 100).toFixed(2)}%</p>
      </div>
    {/if}

    {#if highlightRes && showHighlights}
      <div id="highlighted-text" class="result-card">
        <button class="tile-close-btn" onclick={() => highlightRes = null} aria-label="Close">&times;</button>
        <h3>Prediction Reasoning</h3>
        <p class="highlight-legend">
          <span class="legend-green">Green</span> → Low fake news probability.<br>
          <span class="legend-red">Red</span> → High fake news probability.
        </p>
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
            </div>
    </div>
  {/if}
</main>