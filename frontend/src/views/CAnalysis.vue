<template>
  <div class="analysis-page">
    <div class="page-header">
      <h1 class="page-title">⚙️ C/C++代码分析</h1>
      <p class="page-subtitle">输入C/C++代码，查看变量和内存布局的可视化效果</p>
    </div>

    <div class="analysis-container">
      <div class="editor-section">
        <div class="section-header">
          <span class="section-title">代码编辑器</span>
          <div class="section-actions">
            <select v-model="selectedExample" @change="loadExample" class="form-control example-select">
              <option value="">选择示例</option>
              <option value="variables">变量声明</option>
              <option value="array">数组操作</option>
              <option value="pointer">指针操作</option>
              <option value="nested">二维数组</option>
            </select>
          </div>
        </div>
        
        <div class="code-editor-wrapper">
          <textarea 
            v-model="codeContent" 
            class="code-textarea"
            placeholder="输入C/C++代码...&#10;&#10;示例：&#10;int main() {&#10;    int a = 10;&#10;    int b = 20;&#10;    int c = a + b;&#10;}"
            spellcheck="false"
          ></textarea>
        </div>

        <div class="editor-footer">
          <button @click="handleRun" class="btn btn-cpp" :disabled="loading">
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

        <div class="visualization-content">
          <div v-if="!visualData" class="empty-state">
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-title">暂无可视化数据</div>
            <div class="empty-state-description">输入代码并点击运行分析，查看变量的内存变化</div>
          </div>

          <div v-else class="memory-blocks">
            <div 
              v-for="variable in currentVariables" 
              :key="variable.name"
              class="memory-block c-style"
              :class="{ 'changed': variable.is_changed }"
            >
              <div class="memory-block-header">
                <span class="memory-block-name">{{ variable.name }}</span>
                <span class="memory-block-address">{{ variable.address }}</span>
              </div>
              <div class="memory-block-value">{{ variable.value !== null ? variable.value : '未初始化' }}</div>
              <div class="memory-block-type">{{ variable.type }}</div>
              <div v-if="variable.is_changed && variable.old_value !== null" class="memory-block-change">
                <span class="change-label">原值:</span>
                <span class="change-old">{{ variable.old_value }}</span>
                <span class="change-arrow">→</span>
                <span class="change-new">{{ variable.value }}</span>
              </div>
            </div>

            <div v-if="currentLists.length > 0" class="lists-section">
              <h4 class="lists-title">数组结构</h4>
              <div v-for="arr in currentLists" :key="arr.name" class="array-container">
                <div class="array-header">
                  <span class="array-name">{{ arr.name }}</span>
                  <span class="array-address">{{ arr.address }}</span>
                  <span class="array-type">{{ arr.type }}</span>
                </div>
                <div class="array-grid">
                  <div 
                    v-for="elem in arr.elements" 
                    :key="elem.index" 
                    class="grid-cell"
                    :class="{ 'nested-cell': elem.is_nested }"
                  >
                    <span class="cell-index">[{{ elem.index }}]</span>
                    <span class="cell-value">{{ elem.value !== null ? elem.value : '0' }}</span>
                    <span class="cell-address">{{ elem.address }}</span>
                    <div v-if="elem.is_nested && elem.nested_elements" class="nested-grid">
                      <div v-for="nested in elem.nested_elements" :key="nested.index" class="nested-cell">
                        <span class="nested-index">[{{ nested.index }}]</span>
                        <span class="nested-value">{{ nested.value !== null ? nested.value : '0' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="currentPointers.length > 0" class="pointers-section">
              <h4 class="pointers-title">指针变量</h4>
              <div v-for="ptr in currentPointers" :key="ptr.name" class="pointer-container">
                <div class="pointer-box">
                  <div class="pointer-header">
                    <span class="pointer-name">{{ ptr.name }}</span>
                    <span class="pointer-address">{{ ptr.address }}</span>
                  </div>
                  <div class="pointer-value">
                    <span class="pointer-label">指向:</span>
                    <span class="pointer-target" :class="{ 'null-pointer': !ptr.points_to }">
                      {{ ptr.points_to || 'NULL' }}
                    </span>
                  </div>
                  <div v-if="ptr.points_to" class="pointer-arrow">
                    <svg width="100%" height="30" viewBox="0 0 200 30">
                      <path d="M0,15 L180,15" stroke="#00599C" stroke-width="2" stroke-dasharray="5,5"/>
                      <polygon points="180,15 170,5 170,25" fill="#00599C"/>
                    </svg>
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
const currentStep = ref(0)
const playbackSpeed = ref(1)
const loading = ref(false)
const selectedExample = ref('')

const examples = {
  variables: `int main() {
    int a = 10;
    int b = 20;
    int c = a + b;
    return 0;
}`,
  array: `int main() {
    int arr[5] = {1, 2, 3, 4, 5};
    arr[0] = 99;
    return 0;
}`,
  pointer: `int main() {
    int value = 42;
    int *ptr = &value;
    *ptr = 100;
    return 0;
}`,
  nested: `int main() {
    int matrix[2][3] = {{1, 2, 3}, {4, 5, 6}};
    matrix[0][0] = 100;
    return 0;
}`
}

const totalSteps = computed(() => {
  if (!visualData.value) return 0
  const vars = visualData.value.variables || []
  return vars.length
})

const currentVariables = computed(() => {
  if (!visualData.value?.variables) return []
  return visualData.value.variables[currentStep.value]?.variables || []
})

const currentLists = computed(() => {
  if (!visualData.value?.lists) return []
  return visualData.value.lists[currentStep.value]?.lists || []
})

const currentPointers = computed(() => {
  if (!visualData.value?.variables) return []
  const stepVars = visualData.value.variables[currentStep.value]?.variables || []
  return stepVars.filter(v => v.type?.includes('*'))
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
    const res = await parseApi.parseC(codeContent.value)
    visualData.value = res.data.visuals
    currentStep.value = 0
    
    if (authStore.isAuthenticated) {
      await recordApi.create({
        code_content: codeContent.value,
        language: 'c'
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

.memory-block.c-style {
  background: linear-gradient(135deg, #00599C 0%, #004a85 100%);
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

.lists-section,
.pointers-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.lists-title,
.pointers-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.array-container {
  margin-bottom: 20px;
}

.array-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.array-name {
  font-weight: 600;
  color: var(--primary-color);
}

.array-address {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: var(--text-muted);
}

.array-type {
  font-size: 12px;
  color: var(--cpp-blue);
  font-weight: 500;
}

.array-grid {
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
  background-color: var(--cpp-blue);
  color: white;
}

.grid-cell.nested-cell {
  border: 2px dashed var(--cpp-blue);
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
  background-color: rgba(0, 89, 156, 0.1);
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

.pointer-container {
  margin-bottom: 16px;
}

.pointer-box {
  background: linear-gradient(135deg, rgba(0, 89, 156, 0.1) 0%, rgba(0, 89, 156, 0.05) 100%);
  border: 2px dashed var(--cpp-blue);
  border-radius: var(--radius-md);
  padding: 16px;
}

.pointer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.pointer-name {
  font-weight: 600;
  color: var(--cpp-blue);
}

.pointer-address {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: var(--text-muted);
}

.pointer-value {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pointer-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.pointer-target {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  font-weight: 600;
  color: var(--cpp-blue);
}

.pointer-target.null-pointer {
  color: var(--text-muted);
}

.pointer-arrow {
  margin-top: 8px;
  padding-top: 8px;
}

@media (max-width: 1024px) {
  .analysis-container {
    grid-template-columns: 1fr;
  }
}
</style>
