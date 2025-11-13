<script>
  import {predictAndHighlight} from './lib/api.js'
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from '/vite.svg'

  let text = '';
  let result = null;
  let loading = false;
  let error = '';

  async function analyze() {
    loading = true
    result = null
    error = ''
    
  try {
    result = await predictAndHighlight(text);
  } catch (err) {
    error = 'Error while trying to predict and highlight: ' + err.message;
  } finally {
    loading = false
  }
  }

  // Auto resizing to fit content
  function autoResize(e) {
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }

</script>

<main>
  <h1 class="titletext">Fake News Detector</h1>
  <div class="textinputbox">
    <textarea id="inputbox" on:input={autoResize} bind:value={text} placeholder="Paste a text or link here..."></textarea>
    <button on:click={analyze}>
       {loading ? "Analyzing..." : "Analyze"}
    </button>
  </div>
  <div class="predictionoutput"></div>

</main>

<style>
</style>
