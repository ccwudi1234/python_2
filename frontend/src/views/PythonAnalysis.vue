<template>
  <div class="analysis-page">
    <div class="page-header">
      <h1 class="page-title">🐍 Python代码分析</h1>
      <p class="page-subtitle">输入Python代码，查看变量和内存的可视化效果</p>
    </div>

    <div class="analysis-container">
      <div class="editor-section">
        <div class="section-header">
          <span class="section-title">代码编辑器</span>
          <div class="section-actions">
            <select v-model="selectedExample" @change="loadExample" class="form-control example-select">
              <option value="">选择示例</option>
              <option value="variables">变量赋值</option>
              <option value="list">列表操作</option>
              <option value="copy">拷贝对比</option>
              <option value="nested">嵌套列表</option>
            </select>
          </div>
        </div>
        
        <div class="code-editor-wrapper">
          <textarea 
            v-model="codeContent" 
            class="code-textarea"
            placeholder="输入Python代码..."
            spellcheck="false"
          ></textarea>
        </div>

        <div class="editor-footer">
          <button @click="handleRun" class="btn btn-python" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '分析中...' : '运行分析' }}
          </button>
          <button @click="clearCode" class="btn btn-outline">清空代码</button>
        </div>
      </div>

      <div class="visualization-section">
        <div class="section-header">
          <span class="section-title">可视化效果</span>
          <div class="section-actions">
            <span class="step-info">步骤 {{ currentStep + 1 }} / {{ totalSteps }}</span>
          </div>
        </div>
        
        <div v-if="currentStepInfo" class="step-description">
          {{ currentStepInfo.description }}
        </div>

        <div class="visualization-content">
          <div v-if="!visualData" class="empty-state">
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-title">暂无可视化数据</div>
            <div class="empty-state-description">输入代码并点击运行分析，查看变量的内存变化</div>
          </div>

          <div v-else-if="hasCopyComparison" class="compare-panel">
            <div class="compare-column">
              <div class="compare-column-header compare-column-original">原始对象</div>
              <div class="compare-column-content">
                <div v-if="copyData.original">
                  <div class="var-card">
                    <div class="var-header">
                      <span class="var-name">{{ copyData.original.name }}</span>
                      <span class="var-address">{{ copyData.original.address }}</span>
                    </div>
                    <div class="var-value">{{ copyData.original.type }}</div>
                    <div class="list-items">
                      <div v-for="elem in copyData.original.elements" :key="elem.index" class="list-item">
                        <span class="list-index">{{ elem.index }}</span>
                        <span class="list-value">{{ elem.value }}</span>
                        <span class="list-address">{{ elem.address }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="compare-column">
              <div class="compare-column-header compare-column-shallow">浅拷贝</div>
              <div class="compare-column-content">
                <div v-if="copyData.shallow_copy">
                  <div class="var-card">
                    <div class="var-header">
                      <span class="var-name">{{ copyData.shallow_copy.name }}</span>
                      <span class="var-address">{{ copyData.shallow_copy.address }}</span>
                    </div>
                    <div class="var-value">{{ copyData.shallow_copy.type }}</div>
                    <div class="list-items">
                      <div 
                        v-for="elem in copyData.shallow_copy.elements" 
                        :key="elem.index" 
                        class="list-item"
                        :class="{ 'shared-indicator': elem.is_shared, 'unique-indicator': !elem.is_shared }"
                      >
                        <span class="list-index">{{ elem.index }}</span>
                        <span class="list-value">{{ elem.value }}</span>
                        <span class="list-address">{{ elem.address }}</span>
                        <span v-if="elem.is_shared" class="shared-badge">共享引用</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="compare-column">
              <div class="compare-column-header compare-column-deep">深拷贝</div>
              <div class="compare-column-content">
                <div v-if="copyData.deep_copy">
                  <div class="var-card">
                    <div class="var-header">
                      <span class="var-name">{{ copyData.deep_copy.name }}</span>
                      <span class="var-address">{{ copyData.deep_copy.address }}</span>
                    </div>
                    <div class="var-value">{{ copyData.deep_copy.type }}</div>
                    <div class="list-items">
                      <div 
                        v-for="elem in copyData.deep_copy.elements" 
                        :key="elem.index" 
                        class="list-item"
                        :class="{ 'unique-indicator': !elem.is_shared }"
                      >
                        <span class="list-index">{{ elem.index }}</span>
                        <span class="list-value">{{ elem.value }}</span>
                        <span class="list-address">{{ elem.address }}</span>
                        <span v-if="!elem.is_shared" class="unique-badge">独立对象</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="memory-blocks">
            <div 
              v-for="variable in currentVariables" 
              :key="variable.name"
              class="memory-block"
              :class="{ 'changed': variable.is_changed }"
            >
              <div class="memory-block-header">
                <span class="memory-block-name">{{ variable.name }}</span>
                <span class="memory-block-address">{{ variable.address }}</span>
              </div>
              <div class="memory-block-value">{{ variable.value }}</div>
              <div class="memory-block-type">{{ variable.type }}</div>
              <div v-if="variable.is_changed && variable.old_value !== null" class="memory-block-change">
                <span class="change-label">原值:</span>
                <span class="change-old">{{ variable.old_value }}</span>
                <span class="change-arrow">→</span>
                <span class="change-new">{{ variable.value }}</span>
              </div>
            </div>

            <div v-if="currentLists.length > 0" class="lists-section">
              <h4 class="lists-title">列表结构</h4>
              <div v-for="lst in currentLists" :key="lst.name" class="list-container">
                <div class="list-header">
                  <span class="list-name">{{ lst.name }}</span>
                  <span class="list-address">{{ lst.address }}</span>
                </div>
                <div class="list-grid">
                  <div 
                    v-for="elem in lst.elements" 
                    :key="elem.index" 
                    class="grid-cell"
                    :class="{ 'nested-cell': elem.is_nested }"
                  >
                    <span class="cell-index">{{ elem.index }}</span>
                    <span class="cell-value">{{ elem.value }}</span>
                    <span class="cell-address">{{ elem.address }}</span>
                    <div v-if="elem.is_nested && elem.nested_elements" class="nested-grid">
                      <div v-for="nested in elem.nested_elements" :key="nested.index" class="nested-cell">
                        <span class="nested-index">{{ nested.index }}</span>
                        <span class="nested-value">{{ nested.value }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <ControlBar 
          v-if="visualData"
          :currentStep="currentStep"
          :totalSteps="totalSteps"
          :playbackSpeed="playbackSpeed"
          @step="handleStep"
          @reset="handleReset"
          @play="handlePlay"
          @pause="handlePause"
          @speedChange="handleSpeedChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { parseApi, recordApi } from '../api'
import { useAuthStore } from '../store'
import { ElMessage } from 'element-plus'
import ControlBar from '../components/ControlBar.vue'

const authStore = useAuthStore()
const codeContent = ref('')
const visualData = ref(null)
const copyData = ref(null)
const currentStep = ref(0)
const playbackSpeed = ref(1)
const loading = ref(false)
const selectedExample = ref('')

const examples = {
  variables: `a = 10
b = 20
c = a + b
d = c * 2`,
  list: `numbers = [1, 2, 3, 4, 5]
numbers.append(6)
numbers[0] = 99`,
  copy: `original = [[1, 2], [3, 4]]
shallow = list(original)
deep = [[x for x in row] for row in original]`,
  nested: `matrix = [[1, 2], [3, 4], [5, 6]]
matrix[0][0] = 100
matrix[1][1] = 200`
}

const totalSteps = computed(() => {
  if (!visualData.value?.variables) return 0
  return visualData.value.variables.length
})

const currentVariables = computed(() => {
  if (!visualData.value?.variables || currentStep.value >= visualData.value.variables.length) return []
  const stepData = visualData.value.variables[currentStep.value]
  return stepData?.variables || []
})

const currentStepInfo = computed(() => {
  if (!visualData.value?.variables || currentStep.value >= visualData.value.variables.length) return null
  return visualData.value.variables[currentStep.value]
})

const currentLists = computed(() => {
  if (!visualData.value?.lists || currentStep.value >= visualData.value.lists.length) return []
  const stepData = visualData.value.lists[currentStep.value]
  return stepData?.lists || []
})

const hasCopyComparison = computed(() => {
  return copyData.value?.has_comparison || false
})

const loadExample = () => {
  if (selectedExample.value) {
    codeContent.value = examples[selectedExample.value]
  }
}

const handleRun = async () => {
  if (!codeContent.value.trim()) {
    ElMessage.warning('请输入代码')
    return
  }

  loading.value = true
  try {
    const res = await parseApi.parsePython(codeContent.value)
    visualData.value = res.data.visuals
    
    const compareRes = await parseApi.getCopyComparison(codeContent.value)
    copyData.value = compareRes.data
    
    currentStep.value = 0
    
    if (authStore.isAuthenticated) {
      await recordApi.create({
        code_content: codeContent.value,
        language: 'python'
      })
    }
    
    ElMessage.success('分析完成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '分析失败')
  } finally {
    loading.value = false
  }
}

const clearCode = () => {
  codeContent.value = ''
  visualData.value = null
  copyData.value = null
  currentStep.value = 0
  selectedExample.value = ''
}

const handleStep = (step) => {
  currentStep.value = step
}

const handleReset = () => {
  currentStep.value = 0
}

const handlePlay = () => {
}

const handlePause = () => {
}

const handleSpeedChange = (speed) => {
  playbackSpeed.value = speed
}

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const example = urlParams.get('example')
  if (example && examples[example]) {
    codeContent.value = examples[example]
    selectedExample.value = example
  }
})
</script>

<style scoped>
.analysis-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.analysis-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.editor-section,
.visualization-section {
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: var(--card-background);
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.example-select {
  padding: 6px 12px;
  font-size: 13px;
}

.step-info {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.step-description {
  padding: 12px 20px;
  background-color: var(--python-blue);
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.code-editor-wrapper {
  padding: 16px;
}

.code-textarea {
  width: 100%;
  height: 300px;
  padding: 16px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
  background-color: var(--code-background);
  color: var(--code-text);
  border: none;
  border-radius: var(--radius-md);
  resize: vertical;
  outline: none;
}

.code-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.editor-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.visualization-content {
  padding: 20px;
  min-height: 400px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.memory-blocks {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.memory-block {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
}

.memory-block:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-md);
}

.memory-block.changed {
  animation: pulse 0.5s ease;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.4); }
  50% { box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }
}

.memory-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.memory-block-name {
  font-weight: 600;
  font-size: 16px;
}

.memory-block-address {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  opacity: 0.8;
}

.memory-block-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.memory-block-type {
  font-size: 12px;
  opacity: 0.7;
}

.memory-block-change {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 13px;
}

.change-label {
  opacity: 0.7;
}

.change-old {
  text-decoration: line-through;
  opacity: 0.6;
}

.change-arrow {
  color: var(--success-green);
}

.change-new {
  color: var(--success-green);
  font-weight: 600;
}

.lists-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.lists-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.list-container {
  margin-bottom: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.list-name {
  font-weight: 600;
  color: var(--primary-color);
}

.list-address {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: var(--text-muted);
}

.list-grid {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.grid-cell {
  background-color: var(--card-background);
  border-radius: var(--radius-md);
  padding: 12px;
  min-width: 100px;
  text-align: center;
  transition: all 0.2s ease;
}

.grid-cell:hover {
  background-color: var(--python-blue);
  color: white;
}

.grid-cell.nested-cell {
  border: 2px dashed var(--python-blue);
}

.cell-index {
  font-size: 11px;
  color: var(--text-muted);
  display: block;
}

.cell-value {
  font-size: 16px;
  font-weight: 600;
  display: block;
  margin: 4px 0;
}

.cell-address {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 11px;
  color: var(--text-muted);
  display: block;
}

.nested-grid {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.nested-cell {
  background-color: rgba(55, 118, 171, 0.1);
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  text-align: center;
}

.nested-index {
  font-size: 10px;
  color: var(--text-muted);
  display: block;
}

.nested-value {
  font-size: 12px;
  font-weight: 600;
}

.compare-panel {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.compare-column {
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.compare-column-header {
  padding: 16px;
  text-align: center;
  font-weight: 600;
  color: white;
}

.compare-column-original {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.compare-column-shallow {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.compare-column-deep {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.compare-column-content {
  padding: 16px;
}

.var-card {
  background-color: var(--card-background);
  border-radius: var(--radius-md);
  padding: 12px;
}

.var-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.var-name {
  font-weight: 600;
  color: var(--primary-color);
}

.var-address {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 11px;
  color: var(--text-muted);
}

.var-value {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.list-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background-color: white;
  border-radius: var(--radius-sm);
}

.list-index {
  font-size: 12px;
  color: var(--text-muted);
  min-width: 30px;
}

.list-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
}

.list-address {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 11px;
  color: var(--text-muted);
  margin-left: auto;
}

.shared-indicator {
  background-color: rgba(231, 76, 60, 0.1);
  border-left: 3px solid var(--highlight-red);
}

.unique-indicator {
  background-color: rgba(39, 174, 96, 0.1);
  border-left: 3px solid var(--success-green);
}

.shared-badge,
.unique-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
}

.shared-badge {
  background-color: rgba(231, 76, 60, 0.2);
  color: var(--highlight-red);
}

.unique-badge {
  background-color: rgba(39, 174, 96, 0.2);
  color: var(--success-green);
}

@media (max-width: 1024px) {
  .analysis-container {
    grid-template-columns: 1fr;
  }
  
  .compare-panel {
    grid-template-columns: 1fr;
  }
}
</style>
