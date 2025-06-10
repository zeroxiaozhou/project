<template>
  <div class="home-view">
    <div class="page-title">
      <div class="left">
        <img src="/logo05.png" />
      </div>
      <div class="right">
        <!-- 切换页面 -->
        <el-radio-group v-model="currentPageValue" class="item-1">
          <el-radio-button v-for="option in radioOptions" :key="option.value" :value="option.value">{{ option.name
            }}</el-radio-button>
        </el-radio-group>

        <!-- 展示视觉对象 -->
        <el-dropdown @command="downloadCSV" class="item-1">
          <el-button type="primary">选择导出数据<el-icon class="el-icon--right"><arrow-down /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="(visual, index) in visualList" :key="index" :command="index">
                {{ visual.displayName }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown @command="handleTableChange" class="item-1">
          <el-button type="primary">切换报表<el-icon class="el-icon--right"><arrow-down /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="key in Object.keys(userStore.tablename)" :key="key" :command="key">{{ key
                }}</el-dropdown-item>
              <el-dropdown-item command="logout" style="color: rgba(230, 75, 16, 1);">退出账号</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    <div ref="embedContainer" :style="{ height: '100%', width: '100%' }"></div>
  </div>
  <Watermark />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import * as pbi from 'powerbi-client';
import { useUserStore } from '../store/user';
import service from '../utils/request';
import Watermark from '../components/Watermark.vue';
import { ElMessage, ElLoading } from 'element-plus';
import { ArrowDown } from '@element-plus/icons-vue';
import { tr } from 'element-plus/es/locales.mjs';
const userStore = useUserStore(); // 确保导入了store
const embedContainer = ref(null); // 存储嵌入容器的引用
const radioOptions = ref([]); // 存储页面选项
const currentPageValue = ref(''); // 存储当前选中的页面值
const currentTableKey = ref(''); // 存储当前选中的报表键
const visualList = ref([]); // 存储过滤后的视觉对象
let reportInstance = null; // 存储报表实例
let loadingInstance = null; // 全局加载实例
let tablelist = null; // 存储报表列表
let filters = null; // 存储筛选器

// 不支持导出的视觉对象类型
const UNSUPPORTED_EXPORT_TYPES = [
  'textbox', 
  'image', 
  'shape', 
  'button', 
  'filter', 
  'slicer',
  'pythonVisual',
  'kpi',           // KPI视觉对象通常不支持导出
  'card',          // 卡片视觉对象通常不支持导出
  'gauges',        // 仪表视觉对象
  'multirowcard',  // 多行卡片
  'blank',         // 空白视觉对象
  'video',         // 视频控件
  'rVisual',       // R视觉对象
  'powerbi-visuals-customvisual', // 自定义视觉对象
  'microsoft-maps', // 地图视觉对象
  'timeline',      // 时间线
  'waterfall',     // 瀑布图
  'funnel'         // 漏斗图
];

// 显示加载指示器
const showLoading = () => {
  if (!loadingInstance) {
    loadingInstance = ElLoading.service({
      fullscreen: true,
      text: '加载中...',
      background: 'rgba(0, 0, 0, 0.7)'
    });
  }
};

// 隐藏加载指示器
const hideLoading = () => {
  if (loadingInstance) {
    loadingInstance.close();
    loadingInstance = null;
  }
};

// 导出CSV处理函数
const downloadCSV = async (index) => {
  const visualInfo = visualList.value[index];
  if (!visualInfo || !reportInstance) {
    ElMessage.error('视觉对象不存在');
    return;
  }
  console.log(`尝试导出视觉对象: ${visualInfo.displayName} (${visualInfo.type})`);
  try {
    showLoading();
    // 获取当前活动页面
    const pages = await reportInstance.getPages();
    const activePage = pages.find(page => page.isActive);
    
    if (!activePage) {
      throw new Error('找不到活动页面');
    }
    // 获取指定视觉对象
    const visuals = await activePage.getVisuals();
    const visual = visuals.find(v => v.name === visualInfo.id);
    if (!visual) {
      throw new Error('找不到指定视觉对象');
    }
    // 额外检查：确认视觉类型是否支持导出
    if (UNSUPPORTED_EXPORT_TYPES.includes(visual.type)) {
      throw new Error(`此视觉类型 (${visual.type}) 不支持数据导出`);
    }
    // 使用视觉对象的exportData方法导出数据
    const result = await visual.exportData(
      pbi.models.ExportDataType.Summarized, // 导出汇总数据
      10000 // 最大行数
    );
    // 生成文件名
    const fileName = `${visualInfo.displayName.replace(/[\\/:*?"<>|]/g, '')}.csv`;
    // 创建并下载文件
    const blob = new Blob(["\uFEFF" + result.data], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    ElMessage.success('导出成功');
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error(`这个没数据,换一个`);
  } finally {
    hideLoading();
  }
};

const loadReport = async (tableKey) => {
  try {
    const response = await service.post('/embed_token', { tablename: tableKey });
    if (!response.data?.embed_token?.token || 
        !response.data?.embed_url || 
        !response.data?.report_id) {
      throw new Error('无效的嵌入配置参数');
    }
    
    const config = {
      type: 'report',
      tokenType: pbi.models.TokenType.Embed,
      accessToken: response.data.embed_token.token,
      embedUrl: response.data.embed_url,
      id: response.data.report_id,
      permissions: pbi.models.Permissions.All,
      settings: {
        panes: {
          filters: { visible: false },
          pageNavigation: { visible: false }
        },
        bars: {
          statusBar: { visible: false }
        }
      }
    };
    reportInstance = window.powerbi.embed(embedContainer.value, config);
    reportInstance.on('loaded', async () => {
      try {
        console.log("报表加载完成");
        if (filters["兵团"] && Object.keys(filters["兵团"]).length > 0) {
          const newFilter = {
            $schema: "http://powerbi.com/product/schema#basic",
            filterType: 1,
            operator: "In",
            requireSingleSelection: false,
            target: { 
              table: '城市信息数据', 
              column: '兵团' 
            },
            values: Object.values(filters["兵团"])
          };
          await reportInstance.setFilters([newFilter]);
          // console.log('筛选器成功设置');
        }
        const pages = await reportInstance.getPages();
        radioOptions.value = tablelist[tableKey].map((item, index) => ({
          name: item,
          value: `item${index}`
        }));
        if (tablelist[tableKey].length > 0) {
          currentPageValue.value = radioOptions.value[0].value;
          // 加载完成后立即切换到第一个页面并获取视觉对象
          await switchToPage(currentPageValue.value);
        }
        hideLoading();
      } catch (error) {
        console.error("页面初始化失败:", error);
        ElMessage.error('页面初始化失败');
        hideLoading();
      }
    });
  } catch (error) {
    console.error('报表加载失败:', error);
    ElMessage.error(`报表加载失败: ${error.message}`);
    hideLoading();
  }
};

// 切换报表处理函数
const handleTableChange = async (selectedKey) => {
  if (selectedKey === "logout") {
    userStore.logout();
    window.location.href = '/powerbi/';
    return;
  }
  
  try {
    showLoading();
    currentTableKey.value = selectedKey;
    visualList.value = [];
    
    // 销毁旧报表实例
    if (reportInstance) {
      reportInstance.off('loaded');
      reportInstance.off('rendered');
      window.powerbi.reset(embedContainer.value);
    }
    
    await loadReport(selectedKey);
  } catch (error) {
    ElMessage.error('报表切换失败');
    hideLoading();
  }
};

// 切换页面处理函数
const switchToPage = async (pageValue) => {
  if (!reportInstance) return;
  
  // 检查当前页面是否已经是目标页面
  const activePage = await reportInstance.getActivePage();
  const selectedOption = radioOptions.value.find(option => option.value === pageValue);
  
  if (activePage && activePage.displayName === selectedOption.name) {
    // 如果已经是当前页面，只更新视觉对象列表
    try {
      const visuals = await activePage.getVisuals();
      updateVisualList(visuals);
    } catch (error) {
      console.error("获取视觉对象失败:", error);
    }
    return;
  }

  try {
    showLoading();
    const pages = await reportInstance.getPages();
    const targetPage = pages.find(page => page.displayName === selectedOption.name);
    
    if (targetPage) {
      await targetPage.setActive();
      const visuals = await targetPage.getVisuals();
      updateVisualList(visuals);
    }

    hideLoading();
  } catch (error) {
    console.error("页面切换失败:", error);
    ElMessage.error('页面切换失败');
    hideLoading();
  }
};

// 更新视觉对象列表
const updateVisualList = (visuals) => {
  // 收集所有视觉类型用于调试
  // const allVisualTypes = [...new Set(visuals.map(v => v.type))];
  visualList.value = visuals
    .filter(visual => {
      const isSupported = !UNSUPPORTED_EXPORT_TYPES.includes(visual.type);
      if (!isSupported) {
        // console.log(`过滤掉不支持导出的视觉对象: ${visual.title || visual.name} (${visual.type})`);
      }
      return isSupported;
    })
    .map(visual => ({
      id: visual.name,
      displayName: visual.title || `视觉对象 (${visual.type})`,
      type: visual.type
    }));
};

// 初始化
onMounted(async () => {
  try {
    await userStore.hydrate();
    tablelist = userStore.tablename;
    filters = userStore.filter;
    const firstTableKey = Object.keys(tablelist)[0];
    currentTableKey.value = firstTableKey;
    await loadReport(firstTableKey);
  } catch (error) {
    console.error('初始化失败:', error);
    ElMessage.error('初始化失败，请刷新或重新登录');
    hideLoading();
  }
});

// 监听currentPageValue变化，切换页面
watch(currentPageValue, (newVal) => {
  if (newVal) {
    switchToPage(newVal);
  }
});
</script>

<style scoped>
.home-view {
  width: 100%;
  height: 100vh;
}
.page-title {
  width: 100%;
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.left {
  height: 100%;
  width: 120px;
  /* border: 1px solid red;  */
}
.right {
 /* border: 1px solid red;  */
  display: flex;
  align-items: center;
  gap: 10px;
}
img {
  height: 100%;
  height: 100%;
}
.item-1{
  margin-right: 10px;
}
</style>