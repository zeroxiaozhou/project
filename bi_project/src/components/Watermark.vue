<template>
  <div ref="watermarkEl" class="watermark-container"></div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useUserStore } from '../store/user' // 假设userStore在这个路径下，你需要根据实际情况修改
const props = defineProps({
  leftMargin: {
    type: Number,
    default: 40
  },
  minRightMargin: {
    type: Number,
    default: 0
  }
})

const watermarkEl = ref(null)
const windowWidth = ref(window.innerWidth)
const userStore = useUserStore()

const handleResize = () => {
  windowWidth.value = window.innerWidth
  createWatermark()
}
// 判断窗口宽度是否小于900像素，如果是，则将leftMargin设置为10，否则设置为props.leftMargin
const responsiveLeftMargin = computed(() => {
  return windowWidth.value < 900? 10 : props.leftMargin
})
// 判断窗口宽度是否小于900像素，如果是，则将fontSize设置为10，否则设置为18
const responsiveFontSize = computed(() => {
  return windowWidth.value < 900? 10 : 20
})
// 判断窗口宽度是否小于900像素，如果是，则将rows和cols设置为3，否则设置为4
const responsirows = computed(() => {
  return windowWidth.value < 900? 3 : 5
})
const responsicols = computed(() => {
  return windowWidth.value < 900? 3 : 8
})

const createWatermark = () => {
  if (!watermarkEl.value) return
  watermarkEl.value.innerHTML = ''

  const now = new Date()
  // 格式化日期和时间为yyyy-MM-dd HH:mm:ss格式
  const timeStr = `${(now.getMonth() + 1).toString().padStart(2, '0')}-${
    now.getDate().toString().padStart(2, '0')
  } ${now.getHours().toString().padStart(2, '0')}:${
    now.getMinutes().toString().padStart(2, '0')
  }`

  // 这是水印的参数
  const config = {
    text: `${userStore.username} ${timeStr}`, // 修改为从userStore中获取用户名
    rows: responsirows.value,
    cols: responsicols.value,
    rotate: 15,
    opacity: 0.25,
    fontSize: responsiveFontSize.value,
    leftMargin: responsiveLeftMargin.value,
    minRightMargin: props.minRightMargin
  }

  // 这里是计算水印的宽度和高度
  const rad = config.rotate * Math.PI / 180
  const textWidth = config.text.length * config.fontSize * 0.6
  const textHeight = config.fontSize * 18
  const elementWidth = Math.abs(textWidth * Math.cos(rad)) + Math.abs(textHeight * Math.sin(rad))
  const elementHeight = Math.abs(textWidth * Math.sin(rad)) + Math.abs(textHeight * Math.cos(rad))

  // 计算距离两边的距离
  const availableWidth = window.innerWidth - config.leftMargin - config.minRightMargin
  const colWidth = availableWidth / config.cols
  const rowHeight = window.innerHeight / config.rows

  for (let row = 0; row < config.rows; row++) {
    for (let col = 0; col < config.cols; col++) {
      const span = document.createElement('span')
      span.textContent = config.text

      const left = config.leftMargin + col * colWidth
      const top = row * rowHeight + rowHeight / 2 - elementHeight / 2

      Object.assign(span.style, {
        left: `${left}px`,
        top: `${top}px`,
        transform: `rotate(${config.rotate}deg)`,
        opacity: config.opacity,
        fontSize: `${config.fontSize}px`,
        color: `rgba(129, 135, 139, ${config.opacity})`,
        fontWeight: 'bold',
        whiteSpace: 'nowrap',
        userSelect: 'none',
        transformOrigin: 'left center',
        paddingRight: '10px',
        backfaceVisibility: 'hidden',
        position: 'absolute'
      })

      watermarkEl.value.appendChild(span)
    }
  }
}

onMounted(() => {
  userStore.hydrate() // 从localStorage恢复用户信息
  createWatermark()
  window.addEventListener('resize', handleResize)
  userStore.$subscribe(() => {
    // console.log('用户名已更新，重新生成水印')
    createWatermark()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style>
.watermark-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: visible;
  z-index: 999;
}
</style>