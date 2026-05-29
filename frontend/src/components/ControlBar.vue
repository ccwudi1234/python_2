<template>
  <div class="control-bar">
    <el-button-group>
      <el-button @click="handleReset" :disabled="!hasData">
        <el-icon><RefreshLeft /></el-icon>重置
      </el-button>
      <el-button @click="handlePrev" :disabled="currentStep === 0 || !hasData">
        <el-icon><DArrowLeft /></el-icon>上一步
      </el-button>
      <el-button type="primary" @click="togglePlay" :disabled="!hasData">
        <el-icon v-if="!isPlaying"><VideoPlay /></el-icon>
        <el-icon v-else><VideoPause /></el-icon>
        {{ isPlaying ? '暂停' : '播放' }}
      </el-button>
      <el-button @click="handleNext" :disabled="!hasData || currentStep >= totalSteps - 1">
        下一步<el-icon><DArrowRight /></el-icon>
      </el-button>
    </el-button-group>
    
    <div class="speed-control">
      <span class="label">速度:</span>
      <el-slider
        v-model="speed"
        :min="200"
        :max="3000"
        :step="100"
        :format-tooltip="formatSpeed"
        style="width: 150px"
      />
    </div>
    
    <div class="step-display" v-if="hasData">
      <el-tag>步骤 {{ currentStep + 1 }} / {{ totalSteps }}</el-tag>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  totalSteps: { type: Number, default: 0 },
  initialStep: { type: Number, default: 0 }
})

const emit = defineEmits(['step', 'reset', 'play', 'pause', 'speedChange'])

const currentStep = ref(props.initialStep)
const isPlaying = ref(false)
const speed = ref(1000)
let playTimer = null

const hasData = computed(() => props.totalSteps > 0)

watch(() => props.initialStep, (val) => {
  currentStep.value = val
})

watch(isPlaying, (val) => {
  if (val) {
    startPlay()
    emit('play')
  } else {
    stopPlay()
    emit('pause')
  }
})

watch(speed, (val) => {
  emit('speedChange', (3200 - val) / 1000)
})

function startPlay() {
  if (playTimer) clearInterval(playTimer)
  playTimer = setInterval(() => {
    if (currentStep.value < props.totalSteps - 1) {
      currentStep.value++
      emit('step', currentStep.value)
    } else {
      isPlaying.value = false
    }
  }, speed.value)
}

function stopPlay() {
  if (playTimer) {
    clearInterval(playTimer)
    playTimer = null
  }
}

function togglePlay() {
  isPlaying.value = !isPlaying.value
}

function handlePrev() {
  if (currentStep.value > 0) {
    currentStep.value--
    emit('step', currentStep.value)
    isPlaying.value = false
  }
}

function handleNext() {
  if (currentStep.value < props.totalSteps - 1) {
    currentStep.value++
    emit('step', currentStep.value)
    isPlaying.value = false
  }
}

function handleReset() {
  currentStep.value = 0
  emit('reset')
  isPlaying.value = false
}

function formatSpeed(val) {
  return `${(3200 - val) / 1000}x`
}

onUnmounted(() => {
  stopPlay()
})
</script>

<style scoped>
.control-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 12px 20px;
  background: #fff;
  border-top: 1px solid var(--border-color);
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.speed-control .label {
  color: #64748b;
  font-size: 14px;
}

.step-display {
  margin-left: auto;
}
</style>
