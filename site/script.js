const revealItems = document.querySelectorAll('.reveal');

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
      }
    });
  },
  { threshold: 0.18 }
);

revealItems.forEach((item) => {
  revealObserver.observe(item);
  if (item.getBoundingClientRect().top < window.innerHeight * 0.92) {
    item.classList.add('is-visible');
  }
});


function setLanguage(language) {
  document.documentElement.lang = language === 'en' ? 'en' : 'zh-CN';
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    const nextText = node.dataset[language];
    if (nextText) {
      node.textContent = nextText;
    }
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {
    const nextText = node.dataset[`${language}Placeholder`];
    if (nextText) node.setAttribute('placeholder', nextText);
  });
  document.querySelectorAll('[data-i18n-aria]').forEach((node) => {
    const nextText = node.dataset[`${language}Aria`];
    if (nextText) node.setAttribute('aria-label', nextText);
  });
  document.querySelectorAll('[data-lang-toggle]').forEach((button) => {
    button.textContent = language === 'en' ? '中' : 'EN';
    button.setAttribute('aria-label', language === 'en' ? '切换中文' : 'Switch to English');
  });
  localStorage.setItem('asa-language', language);
}

const savedLanguage = localStorage.getItem('asa-language') || 'en';
setLanguage(savedLanguage);

document.querySelectorAll('[data-lang-toggle]').forEach((button) => {
  button.addEventListener('click', () => {
    const current = localStorage.getItem('asa-language') || 'en';
    setLanguage(current === 'en' ? 'zh' : 'en');
  });
});

const surfaceTabs = document.querySelectorAll('[data-surface-tab]');
const surfacePanes = document.querySelectorAll('[data-surface-pane]');
const homeRoutePreferenceKey = 'asa-route-preference';
const runCountKey = 'asa-demo-run-count';
const savedModelConfigKey = 'asa-saved-model-config';
const bridgeBaseUrl = 'http://localhost:8765';

function setSurface(surface) {
  surfaceTabs.forEach((tab) => {
    const isActive = tab.dataset.surfaceTab === surface;
    tab.classList.toggle('is-active', isActive);
    tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
  });
  surfacePanes.forEach((pane) => {
    pane.classList.toggle('is-active', pane.dataset.surfacePane === surface);
  });
}

surfaceTabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    setSurface(tab.dataset.surfaceTab);
    if (['cinema', 'repo', 'report'].includes(tab.dataset.surfaceTab)) {
      localStorage.setItem(homeRoutePreferenceKey, tab.dataset.surfaceTab);
    }
  });
});

const analyzeConsole = document.querySelector('[data-analyze-console]');
const analyzeButton = document.querySelector('[data-run-analysis]');
const sampleButton = document.querySelector('[data-load-sample]');
const githubInput = document.querySelector('[data-github-input]');
const analyzeState = document.querySelector('[data-analyze-state]');
const consoleLog = document.querySelector('[data-console-log]');
const agentSteps = Array.from(document.querySelectorAll('[data-agent-step]'));
const resultHandoff = document.querySelector('[data-result-handoff]');
const surfaceBoard = document.querySelector('[data-surface-board]');
const modelOptions = Array.from(document.querySelectorAll('[data-model-option]'));
const modelLabel = document.querySelector('[data-model-label]');
const configHint = document.querySelector('[data-config-hint]');
const modelSelector = document.querySelector('[data-model-selector]');
const modelToggle = document.querySelector('[data-model-toggle]');
const saveModelConfigButton = document.querySelector('[data-save-model-config]');
const clearModelConfigButton = document.querySelector('[data-clear-model-config]');
const modelConfigFields = {
  config: document.querySelector('[data-model-config-field="config"]'),
  keyEnv: document.querySelector('[data-model-config-field="keyEnv"]'),
  baseUrl: document.querySelector('[data-model-config-field="baseUrl"]'),
  modelId: document.querySelector('[data-model-config-field="modelId"]'),
  apiKey: document.querySelector('[data-model-config-field="apiKey"]'),
};
const sampleUrls = [
  'https://github.com/anthropics/skills',
  'https://github.com/modelscope/modelscope-agent',
  'https://github.com/simota/agent-skills'
];
let sampleIndex = 0;
let analyzeTimer;
const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

function appendLog(label, message) {
  if (!consoleLog) return;
  const row = document.createElement('p');
  const tag = document.createElement('span');
  const text = document.createElement('strong');
  tag.textContent = label;
  text.textContent = message;
  row.append(tag, text);
  consoleLog.append(row);
  while (consoleLog.children.length > 6) {
    consoleLog.removeChild(consoleLog.firstElementChild);
  }
}

function appendBridgeLogs(logs, seenCount) {
  const nextLogs = Array.isArray(logs) ? logs.slice(seenCount) : [];
  nextLogs.forEach((entry) => appendLog(entry.stage || 'bridge', entry.message || 'working'));
  return seenCount + nextLogs.length;
}

function stepIndexForStage(stage) {
  const stageName = String(stage || '').toLowerCase();
  if (['queued', 'config', 'collect'].includes(stageName)) return 0;
  if (['model', 'route'].includes(stageName)) return 1;
  if (['run', 'analyze'].includes(stageName)) return 3;
  if (['review', 'quality'].includes(stageName)) return 4;
  if (['export', 'ready'].includes(stageName)) return 5;
  return -1;
}

function normalizeErrorMessage(error) {
  const raw = String(error?.message || error || 'analysis failed');
  const firstLine = raw.split(/\r?\n/).find(Boolean) || raw;
  return firstLine.length > 180 ? `${firstLine.slice(0, 177)}...` : firstLine;
}

function setAgentStep(activeIndex) {
  agentSteps.forEach((step, index) => {
    step.classList.toggle('is-active', index === activeIndex);
    step.classList.toggle('is-complete', index < activeIndex);
  });
}


function currentModelConfig() {
  const activeModel = document.querySelector('[data-model-option].is-active');
  return {
    label: modelLabel?.textContent || activeModel?.dataset.model || 'selected model',
    config: modelConfigFields.config?.value.trim() || activeModel?.dataset.config || 'anatomy.config.example.yaml',
    keyEnv: modelConfigFields.keyEnv?.value.trim() || activeModel?.dataset.keyEnv || 'local/no-key',
    baseUrl: modelConfigFields.baseUrl?.value.trim() || activeModel?.dataset.baseUrl || 'local',
    modelId: modelConfigFields.modelId?.value.trim() || activeModel?.dataset.modelId || 'mock',
    provider: activeModel?.dataset.provider || 'mock',
    apiMode: activeModel?.dataset.apiMode || '',
    apiKey: modelConfigFields.apiKey?.value.trim() || '',
  };
}

function syncConfigHint() {
  const config = currentModelConfig();
  if (configHint) configHint.textContent = `python -m asa run --config ${config.config}`;
}

function setModelDrawer(open) {
  if (!modelSelector || !modelToggle) return;
  modelSelector.classList.toggle('is-collapsed', !open);
  modelToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
}

function applyModelOption(option, { preserveKey = false } = {}) {
  const modelName = option.dataset.model || option.textContent.trim();
  if (modelLabel) modelLabel.textContent = modelName;
  if (modelConfigFields.config) modelConfigFields.config.value = option.dataset.config || 'anatomy.config.example.yaml';
  if (modelConfigFields.keyEnv) modelConfigFields.keyEnv.value = option.dataset.keyEnv || 'OPENAI_API_KEY';
  if (modelConfigFields.baseUrl) modelConfigFields.baseUrl.value = option.dataset.baseUrl || 'local';
  if (modelConfigFields.modelId) modelConfigFields.modelId.value = option.dataset.modelId || 'mock';
  if (modelConfigFields.apiKey && !preserveKey) modelConfigFields.apiKey.value = '';
  syncConfigHint();
}

function saveModelConfig() {
  const activeModel = document.querySelector('[data-model-option].is-active');
  const config = currentModelConfig();
  localStorage.setItem(savedModelConfigKey, JSON.stringify({
    activeModel: activeModel?.dataset.model || config.label,
    config: config.config,
    keyEnv: config.keyEnv,
    baseUrl: config.baseUrl,
    modelId: config.modelId,
    provider: config.provider,
    apiMode: config.apiMode,
    apiKey: config.apiKey,
  }));
  appendLog('config', 'model route saved locally');
}

function restoreModelConfig() {
  const raw = localStorage.getItem(savedModelConfigKey);
  if (!raw) return;
  try {
    const saved = JSON.parse(raw);
    const option = modelOptions.find((item) => item.dataset.model === saved.activeModel || item.dataset.modelId === saved.modelId);
    if (option) {
      modelOptions.forEach((item) => {
        const active = item === option;
        item.classList.toggle('is-active', active);
        item.setAttribute('aria-checked', active ? 'true' : 'false');
      });
      applyModelOption(option, { preserveKey: true });
    }
    if (modelLabel) modelLabel.textContent = saved.activeModel || saved.modelId || modelLabel.textContent;
    if (modelConfigFields.config) modelConfigFields.config.value = saved.config || modelConfigFields.config.value;
    if (modelConfigFields.keyEnv) modelConfigFields.keyEnv.value = saved.keyEnv || '';
    if (modelConfigFields.baseUrl) modelConfigFields.baseUrl.value = saved.baseUrl || modelConfigFields.baseUrl.value;
    if (modelConfigFields.modelId) modelConfigFields.modelId.value = saved.modelId || modelConfigFields.modelId.value;
    if (modelConfigFields.apiKey) modelConfigFields.apiKey.value = saved.apiKey || '';
    syncConfigHint();
  } catch {
    localStorage.removeItem(savedModelConfigKey);
  }
}


function preferredCompletionSurface() {
  const runCount = Number(localStorage.getItem(runCountKey) || '0');
  if (runCount <= 0) return 'cinema';
  return localStorage.getItem(homeRoutePreferenceKey) || 'repo';
}

function runCompletionHandoff(forcedSurface) {
  const surface = forcedSurface || preferredCompletionSurface();
  resultHandoff?.classList.add('is-visible');
  resultHandoff?.setAttribute('data-route', surface);
  resultHandoff?.querySelector('[data-handoff-route]')?.setAttribute('href', surface === 'cinema' ? 'cinema/' : 'repo/');
  setSurface(surface);
  setTimeout(() => {
    document.querySelector('#surfaces')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 420);
  setTimeout(() => {
    surfaceBoard?.classList.add('is-handoff-target');
    document.querySelector(`[data-surface-tab="${surface}"]`)?.classList.add('is-handoff-pulse');
    document.querySelector(`[data-surface-pane="${surface}"] .surface-link`)?.classList.add('is-handoff-pulse');
  }, 980);
  setTimeout(() => {
    surfaceBoard?.classList.remove('is-handoff-target');
    document.querySelector(`[data-surface-tab="${surface}"]`)?.classList.remove('is-handoff-pulse');
    document.querySelector(`[data-surface-pane="${surface}"] .surface-link`)?.classList.remove('is-handoff-pulse');
    localStorage.setItem(runCountKey, String(Number(localStorage.getItem(runCountKey) || '0') + 1));
  }, 3300);
}

async function runDemoAnalysis() {
  if (!analyzeConsole || !githubInput || !analyzeButton) return;
  clearInterval(analyzeTimer);
  const url = githubInput.value.trim() || sampleUrls[0];
  analyzeConsole.classList.add('is-running');
  analyzeConsole.classList.remove('is-complete', 'is-failed');
  resultHandoff?.classList.remove('is-visible');
  analyzeButton.disabled = true;
  if (analyzeState) analyzeState.textContent = 'running';
  consoleLog.innerHTML = '';
  const selectedRoute = currentModelConfig();
  const selectedModel = selectedRoute.label;
  const selectedConfig = selectedRoute.config;
  const selectedKeyEnv = selectedRoute.keyEnv;
  const steps = [
    ['collect', `collecting ${url.replace(/^https?:\/\//, '')}`],
    ['model', `routing analysis through ${selectedModel}`],
    ['config', `using ${selectedConfig} with ${selectedKeyEnv}`],
    ['analyze', 'reading SKILL.md and resources'],
    ['review', 'checking evidence and inference'],
    ['export', 'preparing report surfaces']
  ];
  let index = 0;
  setAgentStep(0);
  appendLog(steps[0][0], steps[0][1]);
  analyzeTimer = setInterval(() => {
    index = Math.min(index + 1, 2);
    setAgentStep(index);
    appendLog(steps[index][0], steps[index][1]);
    if (index >= 2) clearInterval(analyzeTimer);
  }, 1400);
  try {
    const result = await runBridgeAnalysis({ url, selectedRoute, limitSkills: 1 });
    clearInterval(analyzeTimer);
    setAgentStep(steps.length - 1);
    analyzeConsole.classList.remove('is-running');
    analyzeConsole.classList.add('is-complete');
    appendLog('run', `completed ${result.run_id || 'run'}`);
    appendLog('export', 'site report / data / graph refreshed');
    if (analyzeState) analyzeState.textContent = 'ready';
    runCompletionHandoff('cinema');
  } catch (error) {
    clearInterval(analyzeTimer);
    analyzeConsole.classList.remove('is-running');
    analyzeConsole.classList.add('is-failed');
    if (analyzeState) analyzeState.textContent = 'failed';
    appendLog('failed', normalizeErrorMessage(error));
    appendLog('check', 'verify model config, API key, base URL, and network');
  } finally {
    clearInterval(analyzeTimer);
    analyzeButton.disabled = false;
  }
}

async function runBridgeAnalysis({ url, selectedRoute, limitSkills }) {
  const requestBody = {
    github_url: url,
    config_file: selectedRoute.config,
    limit_skills: limitSkills,
    provider: selectedRoute.provider,
    model: selectedRoute.modelId,
    base_url: selectedRoute.baseUrl,
    api_key_env: selectedRoute.keyEnv,
    api_key: selectedRoute.apiKey,
    api_mode: selectedRoute.apiMode,
  };
  try {
    return await runBridgeJob(requestBody);
  } catch (error) {
    if (!error.bridgeUnavailable) throw error;
    appendLog('bridge', `job stream unavailable: ${error.message}`);
    return runBridgeSync(requestBody);
  }
}

async function runBridgeJob(requestBody) {
  const startResponse = await fetch(`${bridgeBaseUrl}/api/analyze/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  });
  const startPayload = await startResponse.json().catch(() => ({}));
  if (!startResponse.ok || !startPayload.ok || !startPayload.job_id) {
    const error = new Error(startPayload.message || `job HTTP ${startResponse.status}`);
    error.bridgeUnavailable = startResponse.status === 404;
    throw error;
  }
  appendLog('job', `queued ${startPayload.job_id}`);
  let seenLogs = 0;
  for (let attempt = 0; attempt < 900; attempt += 1) {
    await sleep(attempt < 10 ? 900 : 1600);
    const pollResponse = await fetch(`${bridgeBaseUrl}/api/analyze/jobs/${encodeURIComponent(startPayload.job_id)}`);
    const job = await pollResponse.json().catch(() => ({}));
    if (!pollResponse.ok || !job.ok) {
      const error = new Error(job.message || `poll HTTP ${pollResponse.status}`);
      error.bridgeUnavailable = pollResponse.status === 404;
      throw error;
    }
    seenLogs = appendBridgeLogs(job.logs, seenLogs);
    const nextStep = stepIndexForStage(job.stage);
    if (nextStep >= 0) setAgentStep(nextStep);
    if (job.status === 'completed') return job;
    if (job.status === 'failed') {
      throw new Error(job.message || 'analysis job failed');
    }
  }
  throw new Error('analysis job timed out');
}

async function runBridgeSync(requestBody) {
  const response = await fetch(`${bridgeBaseUrl}/api/analyze/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || !payload.ok) {
    throw new Error(payload.message || `bridge HTTP ${response.status}`);
  }
  return payload;
}

function finishDemoAnalysisFallback(steps, startIndex) {
  return new Promise((resolve) => {
    let index = startIndex;
    analyzeTimer = setInterval(() => {
      index += 1;
      if (index < steps.length) {
        setAgentStep(index);
        appendLog(steps[index][0], steps[index][1]);
        return;
      }
      clearInterval(analyzeTimer);
      setAgentStep(steps.length - 1);
      analyzeConsole.classList.remove('is-running');
      analyzeConsole.classList.add('is-complete');
      if (analyzeState) analyzeState.textContent = 'ready';
      appendLog('ready', preferredCompletionSurface() === 'cinema' ? 'demo story ready' : 'repo dossier ready');
      runCompletionHandoff();
      resolve();
    }, 520);
  });
}

analyzeButton?.addEventListener('click', runDemoAnalysis);

sampleButton?.addEventListener('click', () => {
  sampleIndex = (sampleIndex + 1) % sampleUrls.length;
  if (githubInput) githubInput.value = sampleUrls[sampleIndex];
  appendLog('sample', sampleUrls[sampleIndex].replace('https://github.com/', 'github.com/'));
});

githubInput?.addEventListener('focus', () => analyzeConsole?.classList.add('is-focused'));
githubInput?.addEventListener('blur', () => analyzeConsole?.classList.remove('is-focused'));

modelToggle?.addEventListener('click', () => {
  setModelDrawer(modelSelector?.classList.contains('is-collapsed'));
});

modelOptions.forEach((option) => {
  option.addEventListener('click', () => {
    modelOptions.forEach((item) => {
      const active = item === option;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-checked', active ? 'true' : 'false');
    });
    applyModelOption(option);
    const selectedRoute = currentModelConfig();
    appendLog('model', selectedRoute.label);
    appendLog('env', selectedRoute.keyEnv);
  });
});

Object.values(modelConfigFields).forEach((field) => {
  field?.addEventListener('input', syncConfigHint);
});

saveModelConfigButton?.addEventListener('click', saveModelConfig);
clearModelConfigButton?.addEventListener('click', () => {
  localStorage.removeItem(savedModelConfigKey);
  appendLog('config', 'saved model route cleared');
});

restoreModelConfig();
syncConfigHint();
const settingsPresets = Array.from(document.querySelectorAll('[data-settings-preset]'));
const settingsLabel = document.querySelector('[data-settings-label]');
const settingsLog = document.querySelector('[data-settings-log]');
const settingsFields = {
  provider: document.querySelector('[data-settings-field="provider"]'),
  model: document.querySelector('[data-settings-field="model"]'),
  base: document.querySelector('[data-settings-field="base"]'),
  env: document.querySelector('[data-settings-field="env"]'),
  key: document.querySelector('[data-settings-field="key"]'),
  config: document.querySelector('[data-settings-field="config"]'),
};
const configPreview = document.querySelector('[data-config-preview]');

function appendSettingsLog(label, message) {
  if (!settingsLog) return;
  const row = document.createElement('p');
  const tag = document.createElement('span');
  const text = document.createElement('strong');
  tag.textContent = label;
  text.textContent = message;
  row.append(tag, text);
  settingsLog.append(row);
  while (settingsLog.children.length > 4) {
    settingsLog.removeChild(settingsLog.firstElementChild);
  }
}

function routeLabelForSettings(config) {
  const preset = settingsPresets.find((item) => item.dataset.model === config.model && item.dataset.base === config.base);
  return preset?.dataset.label || `${config.provider} · ${config.model}`;
}

function saveSettingsRoute() {
  const config = currentSettingsConfig();
  const label = routeLabelForSettings(config);
  localStorage.setItem(savedModelConfigKey, JSON.stringify({
    activeModel: label,
    config: config.config,
    keyEnv: config.env,
    baseUrl: config.base,
    modelId: config.model,
    provider: config.provider,
    apiMode: config.provider === 'anthropic' ? 'messages' : 'chat_completions',
    apiKey: config.key,
  }));
  appendSettingsLog('save', 'saved to home entry');
}

function restoreSettingsRoute() {
  const raw = localStorage.getItem(savedModelConfigKey);
  if (!raw || !settingsPresets.length) return;
  try {
    const saved = JSON.parse(raw);
    const preset = settingsPresets.find((item) => item.dataset.model === saved.modelId || item.dataset.label === saved.activeModel);
    if (preset) applySettingsPreset(preset);
    if (settingsLabel) settingsLabel.textContent = saved.activeModel || saved.modelId || settingsLabel.textContent;
    if (settingsFields.provider) settingsFields.provider.value = saved.provider || settingsFields.provider.value;
    if (settingsFields.model) settingsFields.model.value = saved.modelId || settingsFields.model.value;
    if (settingsFields.base) settingsFields.base.value = saved.baseUrl || settingsFields.base.value;
    if (settingsFields.env) settingsFields.env.value = saved.keyEnv || settingsFields.env.value;
    if (settingsFields.key) settingsFields.key.value = saved.apiKey || '';
    if (settingsFields.config) settingsFields.config.value = saved.config || settingsFields.config.value;
    updateSettingsPreview();
  } catch {
    localStorage.removeItem(savedModelConfigKey);
  }
}

function currentSettingsConfig() {
  return {
    provider: settingsFields.provider?.value.trim() || 'openai',
    model: settingsFields.model?.value.trim() || 'gpt-5.2',
    base: settingsFields.base?.value.trim() || 'https://api.openai.com/v1',
    env: settingsFields.env?.value.trim() || 'OPENAI_API_KEY',
    key: settingsFields.key?.value.trim() || '',
    config: settingsFields.config?.value.trim() || 'anatomy.local.yaml',
  };
}

function updateSettingsPreview() {
  if (!configPreview) return;
  const config = currentSettingsConfig();
  configPreview.textContent = `# api_key_env is an environment variable name, not the raw key.\nproviders:\n  default:\n    type: ${config.provider}\n    model: ${config.model}\n    base_url: ${config.base}\n    api_key_env: ${config.env}\n\n# .env or local bridge session\n${config.env}=${config.key ? '***provided in local session only***' : '<paste-key-locally>'}\n\n# run\npython -m asa run --config ${config.config}`;
}

function applySettingsPreset(preset) {
  settingsPresets.forEach((item) => item.classList.toggle('is-active', item === preset));
  if (settingsLabel) settingsLabel.textContent = preset.dataset.label || preset.textContent.trim();
  if (settingsFields.provider) settingsFields.provider.value = preset.dataset.provider || 'openai';
  if (settingsFields.model) settingsFields.model.value = preset.dataset.model || '';
  if (settingsFields.base) settingsFields.base.value = preset.dataset.base || '';
  if (settingsFields.env) settingsFields.env.value = preset.dataset.env || '';
  if (settingsFields.config) settingsFields.config.value = preset.dataset.config || 'anatomy.local.yaml';
  updateSettingsPreview();
  appendSettingsLog('route', preset.dataset.label || preset.textContent.trim());
}

settingsPresets.forEach((preset) => {
  preset.addEventListener('click', () => applySettingsPreset(preset));
});

Object.values(settingsFields).forEach((field) => {
  field?.addEventListener('input', updateSettingsPreview);
});

document.querySelector('[data-save-settings-route]')?.addEventListener('click', saveSettingsRoute);

restoreSettingsRoute();

document.querySelector('[data-copy-config]')?.addEventListener('click', async () => {
  updateSettingsPreview();
  const text = configPreview?.textContent || '';
  try {
    await navigator.clipboard?.writeText(text);
    appendSettingsLog('copy', 'configuration copied to clipboard');
  } catch {
    appendSettingsLog('copy', 'configuration preview refreshed');
  }
});

document.querySelector('[data-test-model]')?.addEventListener('click', async () => {
  const config = currentSettingsConfig();
  appendSettingsLog('test', `POST localhost:8765/api/models/test → ${config.model}`);
  try {
    const response = await fetch('http://localhost:8765/api/models/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider: config.provider,
        model: config.model,
        base_url: config.base,
        api_key: config.key,
        api_key_env: config.env,
      }),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || result.ok === false) {
      appendSettingsLog('fail', result.message || `HTTP ${response.status}`);
      return;
    }
    appendSettingsLog('ok', result.message || 'local bridge model test passed');
  } catch (error) {
    appendSettingsLog('local', 'bridge unavailable; start local API before real test');
  }
});

updateSettingsPreview();

const cinema = document.querySelector('[data-cinema]');
const cinemaTitle = document.querySelector('[data-cinema-title]');
const cinemaText = document.querySelector('[data-cinema-text]');
const cinemaProgress = document.querySelector('[data-cinema-progress]');
const cinemaStepItems = Array.from(document.querySelectorAll('[data-cinema-steps] li'));
const cinemaPlayButton = document.querySelector('[data-cinema-play]');
const cinemaScenes = [
  {
    zhTitle: '信号进入仓库',
    enTitle: 'Source signal enters',
    zhText: 'GitHub URL 被解析成来源信号，仓库结构开始显影。',
    enText: 'The GitHub URL becomes a source signal and the repository structure begins to emerge.',
  },
  {
    zhTitle: '文件星云展开',
    enTitle: 'Repository cloud unfolds',
    zhText: 'SKILL.md、脚本、引用和资产从文件树中被识别出来。',
    enText: 'SKILL.md, scripts, references, and assets are identified from the file tree.',
  },
  {
    zhTitle: 'Skill 核心成形',
    enTitle: 'Skill core forms',
    zhText: '触发条件、边界、工具与步骤围绕 SKILL.md 聚合成核心结构。',
    enText: 'Triggers, boundaries, tools, and steps gather around SKILL.md as a core structure.',
  },
  {
    zhTitle: '资源轨道接入',
    enTitle: 'Resource orbits connect',
    zhText: 'scripts、references、assets 作为外层资源轨道连接到 Skill 核心。',
    enText: 'Scripts, references, and assets connect to the skill core as resource orbits.',
  },
  {
    zhTitle: 'Workflow 被追踪',
    enTitle: 'Workflow is traced',
    zhText: '自然语言步骤被抽象成可审计的执行路径。',
    enText: 'Natural-language instructions are abstracted into an auditable execution path.',
  },
  {
    zhTitle: '证据与审查扫过',
    enTitle: 'Evidence and review sweep',
    zhText: '每个推断被证据线固定，review 扫描标记不确定与风险。',
    enText: 'Each inference is grounded by evidence while review scans uncertainty and risk.',
  },
  {
    zhTitle: '复用资产凝结',
    enTitle: 'Reusable assets crystallize',
    zhText: '模式星座成形，并分裂为 Web Report、Obsidian、Data、Graph 四个出口。',
    enText: 'Pattern constellations form and split into Web Report, Obsidian, Data, and Graph surfaces.',
  },
];
let cinemaIndex = 0;
let cinemaPlaying = true;
let cinemaTimer;

function currentLanguage() {
  return localStorage.getItem('asa-language') || 'en';
}

function setCinemaScene(index) {
  if (!cinema) return;
  cinemaIndex = (index + cinemaScenes.length) % cinemaScenes.length;
  const scene = cinemaScenes[cinemaIndex];
  const language = currentLanguage();
  cinema.dataset.scene = String(cinemaIndex);
  if (cinemaTitle) {
    cinemaTitle.dataset.zh = scene.zhTitle;
    cinemaTitle.dataset.en = scene.enTitle;
    cinemaTitle.textContent = language === 'en' ? scene.enTitle : scene.zhTitle;
  }
  if (cinemaText) {
    cinemaText.dataset.zh = scene.zhText;
    cinemaText.dataset.en = scene.enText;
    cinemaText.textContent = language === 'en' ? scene.enText : scene.zhText;
  }
  if (cinemaProgress) cinemaProgress.style.width = `${((cinemaIndex + 1) / cinemaScenes.length) * 100}%`;
  cinemaStepItems.forEach((item, itemIndex) => item.classList.toggle('is-active', itemIndex === cinemaIndex));
}

function startCinemaTimer() {
  if (!cinema) return;
  clearInterval(cinemaTimer);
  if (!cinemaPlaying) return;
  cinemaTimer = setInterval(() => setCinemaScene(cinemaIndex + 1), 3600);
}

if (cinema) {
  setCinemaScene(0);
  startCinemaTimer();
  document.querySelector('[data-cinema-next]')?.addEventListener('click', () => {
    setCinemaScene(cinemaIndex + 1);
    startCinemaTimer();
  });
  document.querySelector('[data-cinema-prev]')?.addEventListener('click', () => {
    setCinemaScene(cinemaIndex - 1);
    startCinemaTimer();
  });
  cinemaPlayButton?.addEventListener('click', () => {
    cinemaPlaying = !cinemaPlaying;
    cinemaPlayButton.textContent = cinemaPlaying ? 'Pause' : 'Play';
    startCinemaTimer();
  });
}

const cinemaModeButtons = Array.from(document.querySelectorAll('[data-cinema-mode-button]'));
const cinemaModes = Array.from(document.querySelectorAll('[data-cinema-mode]'));

function setCinemaMode(mode) {
  cinemaModeButtons.forEach((button) => button.classList.toggle('is-active', button.dataset.cinemaModeButton === mode));
  cinemaModes.forEach((panel) => panel.classList.toggle('is-active', panel.dataset.cinemaMode === mode));
}

cinemaModeButtons.forEach((button) => {
  button.addEventListener('click', () => setCinemaMode(button.dataset.cinemaModeButton));
});

const aeCinema = document.querySelector('[data-ae-cinema]');
const aeCopy = document.querySelector('[data-ae-copy]');
const aeSequence = document.querySelector('[data-ae-sequence]');
const aeTitle = document.querySelector('[data-ae-title]');
const aeText = document.querySelector('[data-ae-text]');
const aeInsights = document.querySelector('[data-ae-insights]');
const aeLinks = document.querySelector('[data-ae-links]');
const aeRepoProfile = document.querySelector('[data-ae-repo-profile]');
const aeRepoSource = document.querySelector('[data-ae-repo-source]');
const aeRepoName = document.querySelector('[data-ae-repo-name]');
const aeSkillSwitcher = document.querySelector('[data-ae-skill-switcher]');
const aeSkillOptions = document.querySelector('[data-ae-skill-options]');
let aeSteps = Array.from(document.querySelectorAll('[data-ae-step]'));
const aeCards = Array.from(document.querySelectorAll('[data-ae-card]'));
const materialButtons = Array.from(document.querySelectorAll('[data-material-button]'));
const layoutButtons = Array.from(document.querySelectorAll('[data-layout-button]'));
const cinemaViewButtons = Array.from(document.querySelectorAll('[data-cinema-view-button]'));
const aeDetailPanel = document.querySelector('[data-ae-detail-panel]');
const aeDetailLabel = document.querySelector('[data-ae-detail-label]');
const aeDetailTitle = document.querySelector('[data-ae-detail-title]');
const aeDetailBody = document.querySelector('[data-ae-detail-body]');
const aeDetailTags = document.querySelector('[data-ae-detail-tags]');
const aeDetailOutputs = document.querySelector('[data-ae-detail-outputs]');
const aeTrustStrip = document.querySelector('[data-ae-trust-strip]');
const aeDetailFacts = document.querySelector('[data-ae-detail-facts]');
const aeDetailItems = document.querySelector('[data-ae-detail-items]');
const aeDetailLink = document.querySelector('[data-ae-detail-link]');
const aeDetailClose = document.querySelector('[data-ae-detail-close]');
let cinemaManifest = null;
let cinemaViewMode = localStorage.getItem('asa-cinema-view') || 'skill';
let activeSkillFocusId = localStorage.getItem('asa-cinema-skill') || '';
let activeCinemaCards = [];
let aeSelectedDetailIndex = -1;
let aeFrameRequested = false;
let aeActiveIndex = -1;


function setCinemaMaterial(material) {
  const nextMaterial = ['frost', 'crystal', 'aurora'].includes(material) ? material : 'frost';
  if (aeCinema) aeCinema.dataset.material = nextMaterial;
  materialButtons.forEach((button) => {
    button.classList.toggle('is-active', button.dataset.materialButton === nextMaterial);
  });
  localStorage.setItem('asa-cinema-material', nextMaterial);
  requestAeCinemaUpdate();
}

materialButtons.forEach((button) => {
  button.addEventListener('click', () => setCinemaMaterial(button.dataset.materialButton));
});

function setCinemaFinalLayout(layout) {
  const nextLayout = ['deck', 'grid', 'shelf'].includes(layout) ? layout : 'grid';
  if (aeCinema) aeCinema.dataset.finalLayout = nextLayout;
  layoutButtons.forEach((button) => {
    button.classList.toggle('is-active', button.dataset.layoutButton === nextLayout);
  });
  localStorage.setItem('asa-cinema-final-layout', nextLayout);
  requestAeCinemaUpdate();
}

layoutButtons.forEach((button) => {
  button.addEventListener('click', () => setCinemaFinalLayout(button.dataset.layoutButton));
});

function clamp(value, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value));
}

function lerp(start, end, amount) {
  return start + (end - start) * amount;
}

function setAeCardStyle(card, values) {
  card.style.setProperty('--card-x', `${values.x.toFixed(2)}px`);
  card.style.setProperty('--card-y', `${values.y.toFixed(2)}px`);
  card.style.setProperty('--card-z', `${values.z.toFixed(2)}px`);
  card.style.setProperty('--card-rx', `${values.rx.toFixed(2)}deg`);
  card.style.setProperty('--card-ry', `${values.ry.toFixed(2)}deg`);
  card.style.setProperty('--card-rz', `${values.rz.toFixed(2)}deg`);
  card.style.setProperty('--card-scale', values.scale.toFixed(3));
  card.style.setProperty('--card-opacity', values.opacity.toFixed(3));
  card.style.setProperty('--card-blur', `${values.blur.toFixed(2)}px`);
  card.style.setProperty('--card-saturation', values.saturation.toFixed(3));
  card.style.zIndex = String(values.zIndex);
}

function baseAeCardState(index, activeIndex, localProgress, reducedMotion) {
  const distance = index - activeIndex;
  const amplitude = reducedMotion ? .28 : 1;
  if (distance === 0) {
    return {
      x: lerp(10, -26, localProgress),
      y: lerp(4, -8, localProgress),
      z: 140,
      rx: (6.2 - localProgress * 12.4) * amplitude,
      ry: (-10.4 + localProgress * 20.8) * amplitude,
      rz: (-2.6 + localProgress * 5.2) * amplitude,
      scale: 1,
      opacity: 1,
      blur: 0,
      saturation: 1.04,
      zIndex: 80,
    };
  }
  if (distance < 0) {
    const depth = Math.min(4, Math.abs(distance));
    return {
      x: -112 - depth * 28,
      y: 34 + depth * 18,
      z: -90 - depth * 90,
      rx: 8 * amplitude,
      ry: (-18 - depth * 4) * amplitude,
      rz: (-9 - depth * 2) * amplitude,
      scale: Math.max(.58, .86 - depth * .08),
      opacity: Math.max(.12, .34 - depth * .06),
      blur: 3 + depth * 1.4,
      saturation: .82,
      zIndex: 30 - depth,
    };
  }
  const incoming = distance === 1 ? localProgress : 0;
  const depth = Math.min(4, distance);
  return {
    x: lerp(260 + depth * 34, 108, incoming),
    y: lerp(92 + depth * 18, 34, incoming),
    z: lerp(-270 - depth * 70, -42, incoming),
    rx: lerp(18, 8, incoming) * amplitude,
    ry: lerp(-34, -18, incoming) * amplitude,
    rz: lerp(13, 5, incoming) * amplitude,
    scale: lerp(.7, .9, incoming),
    opacity: distance === 1 ? lerp(.34, .72, incoming) : Math.max(.06, .2 - depth * .03),
    blur: distance === 1 ? lerp(10, 3, incoming) : 14,
    saturation: .8,
    zIndex: 20 - depth,
  };
}

function finalAeTarget(index, cardCount, stackOrder, layout) {
  if (layout === 'deck') {
    const depth = cardCount - 1 - index;
    return {
      x: 112 + depth * 28,
      y: -76 + depth * 32,
      z: 42 - depth * 22,
      rx: -2,
      ry: -10 + depth * 1.2,
      rz: -2 + depth * 2.8,
      scale: index === cardCount - 1 ? .52 : .42 - depth * .018,
      opacity: Math.max(.46, .9 - depth * .085),
      blur: depth * .35,
      saturation: Math.max(.76, 1 - depth * .04),
      zIndex: 100 - depth,
    };
  }
  if (layout === 'shelf') {
    const col = index % 2;
    const row = Math.floor(index / 2);
    return {
      x: -170 + col * 340,
      y: -214 + row * 220,
      z: 30 + index * 2,
      rx: 0,
      ry: -2.4,
      rz: 0,
      scale: .43,
      opacity: .9,
      blur: 0,
      saturation: 1.04,
      zIndex: 80 + index,
    };
  }
  const gridTargets = [
    { x: -206, y: 138, scale: .34, rz: -.5, opacity: .66 },
    { x: 28, y: 138, scale: .34, rz: .4, opacity: .68 },
    { x: -206, y: -8, scale: .35, rz: .35, opacity: .72 },
    { x: 28, y: -8, scale: .35, rz: -.35, opacity: .76 },
    { x: -206, y: -154, scale: .35, rz: -.25, opacity: .78 },
    { x: 150, y: -144, scale: .5, rz: .18, opacity: .92 },
  ];
  const target = gridTargets[index] || gridTargets[0];
  return {
    x: target.x,
    y: target.y,
    z: 30 + index * 2,
    rx: 0,
    ry: -3.5,
    rz: target.rz,
    scale: target.scale,
    opacity: target.opacity,
    blur: index === cardCount - 1 ? 0 : .28,
    saturation: index === cardCount - 1 ? 1 : .9,
    zIndex: 86 + index,
  };
}

function finalAeCardState(index, cardCount, finalProgress, currentState, layout = 'grid') {
  const stackOrder = cardCount - 1 - index;
  const settleProgress = clamp(finalProgress * cardCount - stackOrder);
  const eased = 1 - Math.pow(1 - settleProgress, 3);
  const waitingOpacity = index === cardCount - 1 ? currentState.opacity : Math.max(.08, .22 - stackOrder * .018);
  const start = settleProgress > 0 ? currentState : {
    x: -148 + stackOrder * 12,
    y: 44 - stackOrder * 5,
    z: -360 + stackOrder * 26,
    rx: 10,
    ry: -28,
    rz: -8,
    scale: .56,
    opacity: waitingOpacity,
    blur: 12,
    saturation: .76,
    zIndex: 18 + stackOrder,
  };
  const target = finalAeTarget(index, cardCount, stackOrder, layout);
  return {
    x: lerp(start.x, target.x, eased),
    y: lerp(start.y, target.y, eased),
    z: lerp(start.z, target.z, eased),
    rx: lerp(start.rx, target.rx, eased),
    ry: lerp(start.ry, target.ry, eased),
    rz: lerp(start.rz, target.rz, eased),
    scale: lerp(start.scale, target.scale, eased),
    opacity: lerp(start.opacity, target.opacity, eased),
    blur: lerp(start.blur, target.blur, eased),
    saturation: lerp(start.saturation, target.saturation, eased),
    zIndex: settleProgress > 0 ? target.zIndex : start.zIndex,
  };
}

function updateAeCopy(activeStep, activeIndex) {
  if (!activeStep) return;
  if (aeActiveIndex !== activeIndex) {
    aeActiveIndex = activeIndex;
    if (aeSequence) aeSequence.textContent = `${String(activeIndex + 1).padStart(2, '0')} / ${String(aeSteps.length).padStart(2, '0')}`;
    if (aeTitle) aeTitle.textContent = activeStep.dataset.title || '';
    if (aeText) aeText.textContent = activeStep.dataset.text || '';
    if (aeInsights) {
      const insightItems = [
        ['输入', activeStep.dataset.input || '待识别来源'],
        ['动作', activeStep.dataset.action || '拆解与归纳'],
        ['产物', activeStep.dataset.output || '可复用资产'],
      ];
      aeInsights.replaceChildren(...insightItems.map(([label, value]) => {
        const row = document.createElement('div');
        const term = document.createElement('dt');
        const detail = document.createElement('dd');
        term.textContent = label;
        detail.textContent = value;
        row.append(term, detail);
        return row;
      }));
    }
    if (aeLinks) {
      aeLinks.replaceChildren(...(activeStep.dataset.links || '').split(';').filter(Boolean).map((linkPair) => {
        const [label, href] = linkPair.split('|');
        const link = document.createElement('a');
        link.textContent = label || '查看';
        link.href = href || '../report/';
        return link;
      }));
    }
    if (aeCopy) {
      aeCopy.classList.remove('is-switching');
      void aeCopy.offsetWidth;
      aeCopy.classList.add('is-switching');
    }
  }
}

function formatRepoSourceLabel(profile, focusName = null) {
  const kind = profile?.run_kind || 'run';
  if (focusName) return `skill focus · ${kind}`;
  return `${profile?.source_label || profile?.source_type || 'source'} · ${kind}`;
}

function applyCinemaManifest(manifest) {
  if (!manifest || !Array.isArray(manifest.stages) || manifest.stages.length === 0) return;
  cinemaManifest = manifest;
  if (manifest.repo_profile) {
    if (aeRepoProfile) aeRepoProfile.dataset.runKind = manifest.repo_profile.run_kind || 'run';
    const focusName = manifest.skill_focus?.name;
    if (aeRepoSource) aeRepoSource.textContent = formatRepoSourceLabel(manifest.repo_profile, focusName);
    if (aeRepoName) aeRepoName.textContent = focusName || manifest.repo_profile.name || manifest.repo_profile.source_name || manifest.run_id || 'Skill Repository';
  }
  manifest.stages.slice(0, aeSteps.length).forEach((stage, index) => {
    const step = aeSteps[index];
    if (!step) return;
    step.dataset.title = stage.title || step.dataset.title || '';
    step.dataset.text = stage.text || step.dataset.text || '';
    step.dataset.input = stage.input || step.dataset.input || '';
    step.dataset.action = stage.action || step.dataset.action || '';
    step.dataset.output = stage.output || step.dataset.output || '';
    step.dataset.links = Array.isArray(stage.links)
      ? stage.links.map((link) => `${link.label || '查看'}|${link.href || '../report/'}`).join(';')
      : step.dataset.links || '';
  });
  setCinemaView(cinemaViewMode, { persist: false });
  updateAeCopy(aeSteps[Math.max(0, aeActiveIndex)] || aeSteps[0], Math.max(0, aeActiveIndex));
  requestAeCinemaUpdate();
}


function getSkillFocuses() {
  return Array.isArray(cinemaManifest?.skill_focuses) ? cinemaManifest.skill_focuses : (cinemaManifest?.skill_focus ? [cinemaManifest.skill_focus] : []);
}

function getActiveSkillFocus() {
  const focuses = getSkillFocuses();
  if (focuses.length === 0) return null;
  return focuses.find((focus) => focus.id === activeSkillFocusId) || focuses[0];
}

function renderSkillSwitcher() {
  const focuses = getSkillFocuses();
  if (!aeSkillSwitcher || !aeSkillOptions) return;
  aeSkillSwitcher.hidden = cinemaViewMode !== 'skill' || focuses.length <= 1;
  aeSkillOptions.replaceChildren(...focuses.map((focus) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = focus.name || focus.id || 'skill';
    button.dataset.skillFocusId = focus.id || '';
    button.classList.toggle('is-active', (focus.id || '') === (getActiveSkillFocus()?.id || ''));
    button.addEventListener('click', () => setActiveSkillFocus(focus.id || ''));
    return button;
  }));
}

function setActiveSkillFocus(skillId) {
  activeSkillFocusId = skillId;
  localStorage.setItem('asa-cinema-skill', skillId);
  renderSkillSwitcher();
  if (cinemaViewMode !== 'skill') setCinemaView('skill');
  else setCinemaView('skill', { persist: false });
}

function getCinemaCardsForView(mode) {
  if (!cinemaManifest) return [];
  if (mode === 'repo') return Array.isArray(cinemaManifest.repo_overview_cards) ? cinemaManifest.repo_overview_cards : (cinemaManifest.repo_cards || []);
  const focus = getActiveSkillFocus();
  return focus?.cards || cinemaManifest.skill_focus?.cards || cinemaManifest.repo_cards || [];
}

function renderCinemaCards(cards) {
  activeCinemaCards = Array.isArray(cards) ? cards : [];
  aeCards.forEach((card, index) => {
    const stage = cinemaManifest?.stages?.[index];
    const display = activeCinemaCards[index] || stage;
    if (!display) return;
    const title = card.querySelector('strong');
    const paragraph = card.querySelector('p');
    const tags = card.querySelector('.ae-card-tags');
    const primaryLink = display.href || (Array.isArray(stage?.links) && stage.links[0] ? stage.links[0].href : null);
    if (title) title.textContent = display.title || stage?.card_title || title.textContent;
    if (paragraph) {
      if (activeCinemaCards[index]) {
        paragraph.innerHTML = `<b>${display.subtitle || 'card'}</b><br>${display.body || ''}`;
      } else {
        paragraph.innerHTML = `<b>输入</b> ${stage.input || '—'}<br><b>分析</b> ${stage.action || '—'}<br><b>产物</b> ${stage.output || '—'}`;
      }
    }
    if (tags) {
      const values = Array.isArray(display.tags) && display.tags.length ? display.tags : [display.key || 'stage'];
      tags.replaceChildren(...values.map((value) => {
        const tag = document.createElement('em');
        tag.textContent = value;
        return tag;
      }));
    }
    if (primaryLink) card.href = primaryLink;
  });
}

function setCinemaView(mode, options = {}) {
  const hasSkill = getSkillFocuses().length > 0;
  const nextMode = mode === 'repo' || (mode === 'skill' && hasSkill) ? mode : 'repo';
  cinemaViewMode = nextMode;
  cinemaViewButtons.forEach((button) => button.classList.toggle('is-active', button.dataset.cinemaViewButton === nextMode));
  if (options.persist !== false) localStorage.setItem('asa-cinema-view', nextMode);
  renderCinemaCards(getCinemaCardsForView(nextMode));
  if (cinemaManifest?.repo_profile) {
    if (aeRepoProfile) aeRepoProfile.dataset.runKind = cinemaManifest.repo_profile.run_kind || 'run';
    const focusName = nextMode === 'skill' ? getActiveSkillFocus()?.name : null;
    if (aeRepoSource) aeRepoSource.textContent = formatRepoSourceLabel(cinemaManifest.repo_profile, focusName);
    if (aeRepoName) aeRepoName.textContent = focusName || cinemaManifest.repo_profile.name || cinemaManifest.repo_profile.source_name || cinemaManifest.run_id || 'Skill Repository';
  }
  renderSkillSwitcher();
  closeAeDetail();
}

cinemaViewButtons.forEach((button) => {
  button.addEventListener('click', () => setCinemaView(button.dataset.cinemaViewButton));
});

async function loadCinemaManifest() {
  if (!aeCinema) return;
  try {
    const response = await fetch('./cinema-data.json', { cache: 'no-store' });
    if (!response.ok) return;
    applyCinemaManifest(await response.json());
  } catch (_) {
    // Static fallback stays in the HTML.
  }
}

function getAeDetailFallback(index) {
  const domCard = aeCards[index];
  if (!domCard) return null;
  return {
    subtitle: `stage ${String(index + 1).padStart(2, '0')}`,
    title: domCard.querySelector('strong')?.textContent?.trim() || 'Repo Card',
    body: domCard.querySelector('p')?.innerText?.replace(/\s+/g, ' ').trim() || '查看该部分的拆解摘要与报告入口。',
    tags: Array.from(domCard.querySelectorAll('.ae-card-tags em')).map((tag) => tag.textContent.trim()).filter(Boolean),
    href: domCard.getAttribute('href') || '../report/',
    facts: [],
  };
}

function setAeDetailSelection(index) {
  aeSelectedDetailIndex = index;
  aeCards.forEach((card, cardIndex) => {
    card.classList.toggle('is-detail-selected', cardIndex === index);
  });
  aeCinema?.classList.toggle('has-detail-open', index >= 0);
}


function renderAeDetailItems(items) {
  if (!aeDetailItems) return;
  const values = Array.isArray(items) ? items : [];
  aeDetailItems.hidden = values.length === 0;
  aeDetailItems.replaceChildren(...values.slice(0, 6).map((item, index) => {
    const row = document.createElement('article');
    row.className = 'ae-detail-item';
    row.dataset.tone = item.tone || 'item';
    const label = document.createElement('span');
    label.textContent = item.label || `item ${index + 1}`;
    const title = document.createElement('strong');
    title.textContent = item.title || 'Untitled finding';
    const body = document.createElement('p');
    body.textContent = item.body || '';
    if (!body.textContent) body.hidden = true;
    row.append(label, title, body);
    return row;
  }));
}

function openAeDetail(index) {
  const card = activeCinemaCards[index] || cinemaManifest?.repo_cards?.[index] || cinemaManifest?.stages?.[index] || getAeDetailFallback(index);
  if (!card || !aeDetailPanel) return;
  aeDetailPanel.dataset.cardIndex = String(index);
  delete aeDetailPanel.dataset.runKind;
  if (aeDetailLabel) aeDetailLabel.textContent = card.subtitle || card.key || `stage ${String(index + 1).padStart(2, '0')}`;
  if (aeDetailTitle) aeDetailTitle.textContent = card.title || card.card_title || 'Repo Card';
  if (aeDetailBody) aeDetailBody.textContent = card.body || card.text || '该模块来自当前 run 的结构化拆解结果。';
  if (aeTrustStrip) {
    aeTrustStrip.hidden = true;
    aeTrustStrip.replaceChildren();
  }
  if (aeDetailFacts) {
    const facts = Array.isArray(card.facts) ? card.facts : [];
    aeDetailFacts.replaceChildren(...facts.slice(0, aeDetailPanel.dataset.cardIndex === 'profile' ? 8 : 4).map((fact) => {
      const row = document.createElement('div');
      const term = document.createElement('dt');
      const detail = document.createElement('dd');
      term.textContent = fact.label || 'Fact';
      detail.textContent = fact.value || '—';
      row.append(term, detail);
      return row;
    }));
  }
  renderAeDetailItems(card.details);
  if (aeDetailTags) {
    const values = Array.isArray(card.tags) ? card.tags : [];
    aeDetailTags.replaceChildren(...values.map((value) => {
      const tag = document.createElement('span');
      tag.textContent = value;
      return tag;
    }));
  }
  if (aeDetailOutputs) {
    aeDetailOutputs.hidden = true;
    aeDetailOutputs.replaceChildren();
  }
  if (aeDetailLink) {
    aeDetailLink.hidden = false;
    aeDetailLink.href = card.href || card.links?.[0]?.href || '../report/';
  }
  aeDetailPanel.classList.add('is-open');
  setAeDetailSelection(index);
}

function closeAeDetail() {
  aeDetailPanel?.classList.remove('is-open');
  setAeDetailSelection(-1);
}

aeDetailClose?.addEventListener('click', closeAeDetail);

function openRepoProfileDetail() {
  if (!cinemaManifest?.repo_profile || !aeDetailPanel) return;
  const profile = cinemaManifest.repo_profile;
  aeDetailPanel.dataset.cardIndex = 'profile';
  aeDetailPanel.dataset.runKind = profile.run_kind || 'run';
  if (aeDetailLabel) aeDetailLabel.textContent = profile.run_kind || profile.source_label || profile.source_type || 'run dossier';
  if (aeDetailTitle) aeDetailTitle.textContent = profile.name || 'Skill Repository';
  if (aeDetailBody) {
    const skillLine = profile.primary_skill ? `Primary skill ${profile.primary_skill}. ` : '';
    aeDetailBody.textContent = `${skillLine}Run ${profile.run_id || 'unknown'} · model ${profile.provider || 'unknown'} · ${profile.status || 'unknown'}. ${profile.run_notice || ''}`;
  }
  if (aeTrustStrip) {
    const trust = Array.isArray(profile.trust) ? profile.trust : [];
    aeTrustStrip.hidden = trust.length === 0;
    aeTrustStrip.replaceChildren(...trust.map((item) => {
      const cell = document.createElement('span');
      cell.dataset.tone = item.tone || 'neutral';
      cell.innerHTML = `<b>${item.value || '0'}</b><em>${item.label || 'metric'}</em>`;
      return cell;
    }));
  }
  if (aeDetailFacts) {
    const facts = Array.isArray(profile.facts) ? profile.facts : [];
    aeDetailFacts.replaceChildren(...facts.slice(0, aeDetailPanel.dataset.cardIndex === 'profile' ? 8 : 4).map((fact) => {
      const row = document.createElement('div');
      const term = document.createElement('dt');
      const detail = document.createElement('dd');
      term.textContent = fact.label || 'Fact';
      detail.textContent = fact.value || '—';
      row.append(term, detail);
      return row;
    }));
  }
  renderAeDetailItems([]);
  if (aeDetailTags) {
    const tags = [profile.source_type, profile.language, profile.status].filter(Boolean);
    aeDetailTags.replaceChildren(...tags.map((value) => {
      const tag = document.createElement('span');
      tag.textContent = value;
      return tag;
    }));
  }
  if (aeDetailOutputs) {
    const outputs = Array.isArray(profile.outputs) ? profile.outputs : [];
    aeDetailOutputs.hidden = outputs.length === 0;
    aeDetailOutputs.replaceChildren(...outputs.map((output) => {
      const link = document.createElement('a');
      link.href = output.href || '../report/';
      link.dataset.outputKind = output.kind || 'output';
      link.innerHTML = `<span>${output.kind || 'output'}</span><strong>${output.label || 'Output'}</strong>`;
      return link;
    }));
  }
  if (aeDetailLink) {
    aeDetailLink.hidden = true;
    aeDetailLink.href = cinemaManifest.report_href || '../report/';
  }
  aeDetailPanel.classList.add('is-open');
  setAeDetailSelection(-1);
  aeCinema?.classList.add('has-detail-open');
}

aeRepoProfile?.addEventListener('click', openRepoProfileDetail);

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && aeDetailPanel?.classList.contains('is-open')) closeAeDetail();
});

aeCards.forEach((card, index) => {
  card.addEventListener('click', (event) => {
    if (!aeCinema?.classList.contains('is-final-stack')) return;
    event.preventDefault();
    openAeDetail(index);
  });
});

function setAeInteractiveTilt(event) {
  if (!aeCinema || !aeCinema.classList.contains('is-final-stack') || aeCinema.dataset.finalLayout !== 'shelf') return;
  const field = document.querySelector('[data-ae-card-field]');
  if (!field) return;
  const rect = field.getBoundingClientRect();
  const pointerX = ((event.clientX - rect.left) / rect.width - .5) * 2;
  const pointerY = ((event.clientY - rect.top) / rect.height - .5) * 2;
  aeCards.forEach((card, index) => {
    const depth = index / Math.max(1, aeCards.length - 1);
    card.style.setProperty('--card-float-x', `${(pointerX * (5 + depth * 8)).toFixed(2)}px`);
    card.style.setProperty('--card-float-y', `${(pointerY * (3 + depth * 4)).toFixed(2)}px`);
    card.style.setProperty('--card-float-z', `${(Math.abs(pointerX) * 4 + Math.abs(pointerY) * 3).toFixed(2)}px`);
    card.style.setProperty('--card-float-rx', `${(-pointerY * (1.2 + depth * .65)).toFixed(2)}deg`);
    card.style.setProperty('--card-float-ry', `${(pointerX * (1.8 + depth * .8)).toFixed(2)}deg`);
    card.style.setProperty('--card-float-rz', `${(pointerX * .18).toFixed(2)}deg`);
  });
}

function resetAeInteractiveTilt() {
  aeCards.forEach((card) => {
    card.style.setProperty('--card-float-x', '0px');
    card.style.setProperty('--card-float-y', '0px');
    card.style.setProperty('--card-float-z', '0px');
    card.style.setProperty('--card-float-rx', '0deg');
    card.style.setProperty('--card-float-ry', '0deg');
    card.style.setProperty('--card-float-rz', '0deg');
  });
}

function updateAeCinemaNow() {
  aeFrameRequested = false;
  if (!aeCinema || aeSteps.length === 0 || aeCards.length === 0) return;
  const rect = aeCinema.getBoundingClientRect();
  const scrollable = Math.max(1, rect.height - window.innerHeight);
  const progress = clamp(-rect.top / scrollable);
  const narrativeEnd = .82;
  const narrativeProgress = clamp(progress / narrativeEnd);
  const finalProgress = clamp((progress - narrativeEnd) / (1 - narrativeEnd));
  const cardCount = aeCards.length;
  const exactIndex = narrativeProgress * cardCount;
  const activeIndex = Math.min(cardCount - 1, Math.floor(exactIndex));
  const localProgress = activeIndex === cardCount - 1 ? clamp(exactIndex - activeIndex) : exactIndex - activeIndex;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  aeCinema.style.setProperty('--ae-progress', progress.toFixed(4));
  aeCinema.style.setProperty('--ae-local', localProgress.toFixed(4));
  aeCinema.style.setProperty('--ae-final', finalProgress.toFixed(4));
  aeCinema.dataset.aeScene = String(activeIndex);
  aeCinema.classList.toggle('is-final-stack', finalProgress > .02);
  if (finalProgress <= .02 && aeSelectedDetailIndex >= 0) closeAeDetail();
  updateAeCopy(aeSteps[activeIndex], activeIndex);
  aeSteps.forEach((step, index) => step.classList.toggle('is-active', index === activeIndex));
  aeCards.forEach((card, index) => {
    const baseState = baseAeCardState(index, activeIndex, localProgress, reducedMotion);
    const state = finalProgress > 0 ? finalAeCardState(index, cardCount, finalProgress, baseState, aeCinema.dataset.finalLayout) : baseState;
    setAeCardStyle(card, state);
    card.classList.toggle('is-active', index === activeIndex && finalProgress < .2);
    card.classList.toggle('is-stacked', finalProgress > .96);
  });
}

function requestAeCinemaUpdate() {
  if (aeFrameRequested) return;
  aeFrameRequested = true;
  window.requestAnimationFrame(updateAeCinemaNow);
}

if (aeCinema) {
  setCinemaMaterial('crystal');
  setCinemaFinalLayout('shelf');
  updateAeCinemaNow();
  loadCinemaManifest();
  aeCinema.addEventListener('pointermove', setAeInteractiveTilt, { passive: true });
  aeCinema.addEventListener('pointerleave', resetAeInteractiveTilt);
  window.addEventListener('scroll', requestAeCinemaUpdate, { passive: true });
  window.addEventListener('resize', requestAeCinemaUpdate);
}



















const repoDossier = document.querySelector('[data-repo-dossier]');
const repoKind = document.querySelector('[data-repo-kind]');
const repoSummary = document.querySelector('[data-repo-summary]');
const repoName = document.querySelector('[data-repo-name]');
const repoSource = document.querySelector('[data-repo-source]');
const repoTrust = document.querySelector('[data-repo-trust]');
const repoBroadcast = document.querySelector('[data-repo-broadcast]');
const repoExtracted = document.querySelector('[data-repo-extracted]');
const repoSkillList = document.querySelector('[data-repo-skill-list]');
const repoCardGrid = document.querySelector('[data-repo-card-grid]');
let repoManifest = null;
let activeRepoSkillId = '';

async function loadRepoDossier() {
  if (!repoDossier) return;
  try {
    const response = await fetch('../cinema/cinema-data.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`manifest ${response.status}`);
    repoManifest = await response.json();
    activeRepoSkillId = repoManifest.skill_focus?.id || repoManifest.skill_focuses?.[0]?.id || '';
    renderRepoDossier();
  } catch (error) {
    if (repoSummary) repoSummary.textContent = '无法读取本次 run manifest，请先运行 demo export。';
  }
}

function activeRepoSkill() {
  const focuses = Array.isArray(repoManifest?.skill_focuses) ? repoManifest.skill_focuses : [];
  return focuses.find((skill) => skill.id === activeRepoSkillId) || repoManifest?.skill_focus || focuses[0] || null;
}

function renderRepoDossier() {
  if (!repoManifest) return;
  const profile = repoManifest.repo_profile || {};
  const skill = activeRepoSkill();
  if (repoKind) repoKind.textContent = `${profile.run_kind || 'run'} · ${skill?.status || 'unknown'}`;
  if (repoSummary) repoSummary.textContent = skill?.summary || profile.run_notice || 'Repo dossier is ready.';
  if (repoName) repoName.textContent = profile.name || repoManifest.run_id || 'Skill Repository';
  if (repoSource) repoSource.textContent = `${profile.source_label || 'source'} · ${profile.primary_skill || skill?.name || 'skill focus'}`;
  if (repoTrust) {
    const trust = Array.isArray(profile.trust) ? profile.trust : [];
    repoTrust.replaceChildren(...trust.map((item) => {
      const cell = document.createElement('span');
      cell.dataset.tone = item.tone || 'neutral';
      cell.innerHTML = `<b>${item.value || '0'}</b><em>${item.label || 'metric'}</em>`;
      return cell;
    }));
  }
  renderRepoBroadcast(profile, skill);
  renderRepoExtracted(skill);
  renderRepoSkillList();
  renderRepoCards(skill);
}

function renderRepoBroadcast(profile, skill) {
  if (!repoBroadcast) return;
  const summary = repoManifest?.summary || {};
  const cards = Array.isArray(skill?.cards) ? skill.cards : [];
  const items = [
    { label: 'repo', value: profile.name || 'repository' },
    { label: 'skill', value: skill?.name || profile.primary_skill || 'skill' },
    { label: 'layers', value: String(cards.length || 6) },
    { label: 'workflow', value: String(summary.workflow_steps || findRepoFact(cards, 'steps') || '—') },
    { label: 'quality', value: skill?.status || summary.status || 'unknown' },
    { label: 'patterns', value: String(summary.patterns ?? '—') },
  ];
  repoBroadcast.replaceChildren(...items.map((item) => {
    const cell = document.createElement('span');
    cell.innerHTML = `<em>${item.label}</em><strong>${item.value}</strong>`;
    return cell;
  }));
}

function renderRepoExtracted(skill) {
  if (!repoExtracted) return;
  const cards = Array.isArray(skill?.cards) ? skill.cards : [];
  const map = new Map(cards.map((card) => [String(card.title || '').toLowerCase(), card]));
  const extracted = [
    ['触发信号', map.get('trigger')?.body || '未提取触发信号'],
    ['能力边界', map.get('boundary')?.body || '未提取边界'],
    ['工具与资源', map.get('tools')?.body || '未提取工具'],
    ['执行流程', map.get('workflow')?.body || '未提取流程'],
    ['证据质量', map.get('evidence')?.body || '未提取证据'],
    ['复用资产', map.get('reuse')?.body || '未提取复用资产'],
  ];
  repoExtracted.replaceChildren(...extracted.map(([label, body], index) => {
    const item = document.createElement('article');
    item.innerHTML = `<b>${String(index + 1).padStart(2, '0')}</b><span>${label}</span><p>${body}</p>`;
    return item;
  }));
}

function findRepoFact(cards, key) {
  for (const card of cards || []) {
    for (const fact of card.facts || []) {
      if (String(fact.label || '').toLowerCase().includes(key)) return fact.value;
    }
  }
  return '';
}

function renderRepoSkillList() {
  if (!repoSkillList) return;
  const focuses = Array.isArray(repoManifest?.skill_focuses) ? repoManifest.skill_focuses : [];
  repoSkillList.replaceChildren(...focuses.map((skill) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'repo-skill-button';
    button.classList.toggle('is-active', skill.id === activeRepoSkillId);
    button.innerHTML = `<strong>${skill.name || skill.id}</strong><span>${skill.status || 'unknown'}</span>`;
    button.addEventListener('click', () => {
      activeRepoSkillId = skill.id || '';
      renderRepoDossier();
    });
    return button;
  }));
}

function renderRepoCards(skill) {
  if (!repoCardGrid) return;
  const cards = Array.isArray(skill?.cards) ? skill.cards : [];
  repoCardGrid.replaceChildren(...cards.map((card, index) => {
    const article = document.createElement('article');
    article.className = 'repo-dossier-slice';
    article.dataset.slice = card.title || `slice-${index}`;
    const facts = Array.isArray(card.facts) ? card.facts : [];
    const details = Array.isArray(card.details) ? card.details : [];
    const readingLabel = repoSliceLabel(card.title, index);
    article.innerHTML = `
      <div class="repo-slice-head"><span>${String(index + 1).padStart(2, '0')}</span><em>${card.subtitle || 'slice'}</em></div>
      <div class="repo-slice-label">${readingLabel}</div>
      <h3>${card.title || 'Slice'}</h3>
      <p>${card.body || 'No summary available.'}</p>
      <dl>${facts.slice(0, 3).map((fact) => `<div><dt>${fact.label || 'fact'}</dt><dd>${fact.value || '—'}</dd></div>`).join('')}</dl>
      <div class="repo-slice-details">${details.slice(0, 5).map((item) => `<section><span>${item.label || 'item'}</span><strong>${item.title || 'Untitled'}</strong>${item.body ? `<p>${item.body}</p>` : ''}</section>`).join('')}</div>
      <a href="${card.href || '../report/'}">查看对应证据</a>
    `;
    return article;
  }));
}

function repoSliceLabel(title, index) {
  const labels = {
    trigger: '触发条件：什么时候应该调用这个 skill',
    boundary: '能力边界：它负责什么 不负责什么',
    tools: '资源工具：依赖哪些模板 文件或脚本',
    workflow: '执行流程：模型按什么步骤完成任务',
    evidence: '证据扎根：哪些结论有原文支撑',
    reuse: '复用资产：哪些模式可以沉淀给下次使用',
  };
  return labels[String(title || '').toLowerCase()] || `拆解层 ${index + 1}`;
}

loadRepoDossier();


const dataSurface = document.querySelector('[data-data-surface]');
const dataTableBody = document.querySelector('[data-data-table] tbody');
const dataCards = document.querySelector('[data-data-cards]');
const dataSource = document.querySelector('[data-data-source]');
const dataSummary = document.querySelector('[data-data-summary]');
const graphSurface = document.querySelector('[data-graph-surface]');
const graphCanvas = document.querySelector('[data-graph-canvas]');
const graphCount = document.querySelector('[data-graph-count]');

async function loadSharedManifestForSurface() {
  const response = await fetch('../cinema/cinema-data.json', { cache: 'no-store' });
  if (!response.ok) throw new Error(`manifest ${response.status}`);
  return response.json();
}

async function renderDataSurface() {
  if (!dataSurface || !dataTableBody) return;
  try {
    const manifest = await loadDataManifestForSurface();
    const rowCounts = manifest.row_counts || {};
    const files = manifest.files || {};
    const rows = Object.entries(files).map(([kind, file]) => [
      kind,
      linkToDataFile(file),
      `${rowCounts[kind] ?? manifest[`${kind}_count`] ?? 'graph'} rows`,
      manifest.schema_version ? `schema ${manifest.schema_version}` : 'exported artifact',
    ]);
    rows.unshift(['run', manifest.run_id || 'unknown', 'data export', 'data_manifest.json']);
    renderDataRows(rows);
    renderDataManifestCards(manifest);
    if (dataSource) dataSource.textContent = 'Source · real export';
    if (dataSummary) dataSummary.textContent = `${manifest.run_id || 'run'} · ${rows.length - 1} files`;
  } catch (error) {
    await renderDataSurfaceFallback();
  }
}

async function loadDataManifestForSurface() {
  const response = await fetch('../data/data_manifest.json', { cache: 'no-store' });
  if (!response.ok) throw new Error(`data manifest ${response.status}`);
  return response.json();
}

function linkToDataFile(file) {
  const path = String(file || '');
  return path ? `<a href="../data/${path}"><code>${path}</code></a>` : '—';
}

function renderDataRows(rows) {
  dataTableBody.replaceChildren(...rows.map((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = row.map((cell) => `<td>${cell}</td>`).join('');
    return tr;
  }));
}

function renderDataManifestCards(manifest) {
  if (!dataCards) return;
  const rowCounts = manifest.row_counts || {};
  const cards = [
    ['Run', manifest.run_id || 'unknown', 'canonical analysis run'],
    ['Skills', rowCounts.skills ?? manifest.skill_count ?? 0, 'skill rows'],
    ['Workflow', rowCounts.workflow_trace ?? 0, 'trace rows'],
    ['Evidence', rowCounts.evidence_audit ?? 0, 'audit rows'],
    ['Reuse', rowCounts.reuse_assets ?? 0, 'asset rows'],
  ];
  dataCards.replaceChildren(...cards.map(([label, value, note]) => {
    const card = document.createElement('article');
    card.className = 'data-manifest-card';
    card.innerHTML = `<span>${label}</span><strong>${value}</strong><p>${note}</p>`;
    return card;
  }));
}

async function renderDataSurfaceFallback() {
  try {
    const manifest = await loadSharedManifestForSurface();
    const profile = manifest.repo_profile || {};
    const rows = [
      ['demo-run', manifest.run_id || 'unknown', profile.run_kind || 'run', profile.run_notice || ''],
      ['demo-repo', profile.name || 'repository', profile.source_label || 'source', profile.primary_skill || 'skill focus'],
      ...((manifest.skill_focuses || []).map((skill) => ['demo-skill', skill.name || skill.id, skill.status || 'unknown', skill.summary || ''])),
      ...((manifest.skill_focus?.cards || []).map((card) => ['demo-slice', card.title || 'slice', card.subtitle || '', card.body || ''])),
    ];
    renderDataRows(rows);
    if (dataSource) dataSource.textContent = 'Source · demo fallback';
    if (dataSummary) dataSummary.textContent = 'cinema-data.json';
  } catch (fallbackError) {
    dataTableBody.innerHTML = '<tr><td>error</td><td>manifest</td><td>unavailable</td><td>Run export-all first.</td></tr>';
  }
}

async function renderGraphSurface() {
  if (!graphSurface || !graphCanvas) return;
  try {
    const graph = await loadGraphDataForSurface();
    const nodes = layoutGraphNodes(graph.nodes || []);
    const edges = Array.isArray(graph.edges) ? graph.edges : [];
    const spine = document.createElement('div');
    spine.className = 'graph-spine';
    const language = localStorage.getItem('asa-language') || 'en';
    const labels = language === 'en' ? ['Run', 'Skill', 'Resources', 'Workflow', 'Evidence', 'Reuse'] : ['运行', 'Skill', '资源', '流程', '证据', '复用'];
    const layerLabels = labels.map((label) => {
      const item = document.createElement('span');
      item.textContent = label;
      return item;
    });
    const nodeMap = new Map(nodes.map((node) => [node.id, node]));
    const edgeSvg = createGraphEdgesSvg(edges.slice(0, 28), nodeMap);
    const nodeEls = nodes.map((node, index) => {
      const el = document.createElement('a');
      el.className = 'graph-node';
      el.dataset.kind = node.type || node.kind || 'node';
      el.href = graphNodeHref(node);
      el.style.left = `${node.x}%`;
      el.style.top = `${node.y}%`;
      el.style.animationDelay = `${index * 45}ms`;
      el.innerHTML = `<span>${node.type || 'node'} · ${node.confidence || node.category || node.status || 'mapped'}</span><strong>${node.label || node.id}</strong><p>${node.path || node.skill_type || node.actor || node.category || 'Mapped from graph-data.json'}</p>`;
      return el;
    });
    graphCanvas.replaceChildren(spine, ...layerLabels, edgeSvg, ...nodeEls);
    if (graphCount) graphCount.textContent = `${nodes.length} nodes · ${edges.length} edges`;
  } catch (error) {
    try {
      await renderGraphSurfaceFallback();
    } catch (fallbackError) {
      if (graphCount) graphCount.textContent = 'graph unavailable';
    }
  }
}

async function loadGraphDataForSurface() {
  const response = await fetch('../data/graph-data.json', { cache: 'no-store' });
  if (!response.ok) throw new Error('graph data unavailable');
  return response.json();
}

function layoutGraphNodes(rawNodes) {
  const groups = {
    run: rawNodes.filter((node) => node.type === 'run'),
    skill: rawNodes.filter((node) => node.type === 'skill'),
    resource: rawNodes.filter((node) => node.type === 'resource'),
    workflow: rawNodes.filter((node) => node.type === 'workflow_step'),
    evidence: rawNodes.filter((node) => node.type === 'evidence'),
    reuse: rawNodes.filter((node) => node.type === 'reuse'),
  };
  return [
    ...positionGraphGroup(groups.run, 9, 50, 50),
    ...positionGraphGroup(groups.skill, 28, 50, 50),
    ...positionGraphGroup(groups.resource.slice(0, 5), 45, 22, 78),
    ...positionGraphGroup(groups.workflow.slice(0, 6), 60, 18, 82),
    ...positionGraphGroup(groups.evidence.slice(0, 5), 76, 22, 78),
    ...positionGraphGroup(groups.reuse.slice(0, 5), 91, 22, 78),
  ];
}

function positionGraphGroup(nodes, x, startY = 20, endY = 80) {
  if (nodes.length === 1) return [{ ...nodes[0], x, y: startY }];
  const count = Math.max(nodes.length, 1);
  const span = endY - startY;
  return nodes.map((node, index) => ({
    ...node,
    x,
    y: startY + (span * index) / Math.max(count - 1, 1),
  }));
}

function graphNodeHref(node) {
  if (node.type === 'skill') return '../report/#skills';
  if (['resource', 'file'].includes(node.type)) return '../report/#manual-composition-detail';
  if (node.type === 'workflow_step') return '../report/#manual-workflow-detail';
  if (node.type === 'reuse') return '../report/#manual-learning-detail';
  if (node.type === 'evidence') return '../report/#manual-evidence-table';
  return '../report/#trust-review';
}

function createGraphEdgesSvg(edges, nodeMap) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.classList.add('graph-edges-svg');
  svg.setAttribute('viewBox', '0 0 100 100');
  svg.setAttribute('preserveAspectRatio', 'none');
  edges.forEach((edge, index) => {
    const source = nodeMap.get(edge.source);
    const target = nodeMap.get(edge.target);
    if (!source || !target) return;
    const dx = target.x - source.x;
    const curve = Math.max(9, Math.min(22, Math.abs(dx) * 0.55));
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.classList.add('graph-edge-path');
    path.dataset.kind = edge.type || 'edge';
    path.setAttribute('d', `M ${source.x} ${source.y} C ${source.x + curve} ${source.y}, ${target.x - curve} ${target.y}, ${target.x} ${target.y}`);
    path.style.animationDelay = `${index * 18}ms`;
    path.setAttribute('vector-effect', 'non-scaling-stroke');
    path.setAttribute('aria-label', edge.type || 'relation');
    svg.appendChild(path);
  });
  return svg;
}

async function renderGraphSurfaceFallback() {
  const manifest = await loadSharedManifestForSurface();
  const skill = manifest.skill_focus || {};
  const cards = Array.isArray(skill.cards) ? skill.cards : [];
  const outputs = manifest.repo_profile?.outputs || [];
  const slicePositions = [
    [38, 28], [58, 28], [38, 45], [58, 45], [38, 62], [58, 62],
  ];
  const outputPositions = [[84, 25], [84, 41], [84, 57], [84, 73]];
  const nodes = [
    { label: manifest.repo_profile?.name || 'Repo', kind: 'repo', x: 15, y: 49, meta: manifest.repo_profile?.run_kind || 'source', body: manifest.repo_profile?.source_label || 'canonical run' },
    { label: skill.name || 'Skill', kind: 'skill', x: 50, y: 12, meta: skill.status || 'focus', body: skill.summary || 'selected skill focus' },
    ...cards.map((card, index) => ({ label: card.title || `Slice ${index + 1}`, kind: 'slice', x: slicePositions[index]?.[0] || 50, y: slicePositions[index]?.[1] || 50, meta: card.subtitle || `slice ${index + 1}`, body: card.body || '' })),
    ...outputs.slice(0, 4).map((output, index) => ({ label: output.label || 'Output', kind: 'output', x: outputPositions[index]?.[0] || 84, y: outputPositions[index]?.[1] || 50, meta: output.kind || 'surface', body: output.href || '' })),
  ];
  const spine = document.createElement('div');
  spine.className = 'graph-spine';
  const layerLabels = ['Repo Source', 'Skill Core', 'Anatomy Slices', 'Output Assets'].map((label) => {
    const item = document.createElement('span');
    item.textContent = label;
    return item;
  });
  const nodeEls = nodes.map((node, index) => {
    const el = document.createElement('a');
    el.className = 'graph-node';
    el.dataset.kind = node.kind;
    el.href = node.kind === 'output' ? (outputs[index - 2 - cards.length]?.href || '../report/') : '../repo/';
    el.style.left = `${node.x}%`;
    el.style.top = `${node.y}%`;
    el.style.animationDelay = `${index * 55}ms`;
    el.innerHTML = `<span>${node.kind} · ${node.meta || 'mapped'}</span><strong>${node.label}</strong><p>${node.body || 'Mapped from the run manifest.'}</p>`;
    return el;
  });
  graphCanvas.replaceChildren(spine, ...layerLabels, ...nodeEls);
  if (graphCount) graphCount.textContent = `${nodes.length} mapped nodes`;
}


renderDataSurface();
renderGraphSurface();
