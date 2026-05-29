<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">代码可视化分析平台</h1>
        <p class="hero-description">将抽象的代码执行过程转化为直观的可视化，让学习和理解编程变得更简单</p>
        <div class="hero-buttons">
          <router-link to="/python" class="btn btn-lg btn-python">
            <span>🐍</span> Python分析
          </router-link>
          <router-link to="/c" class="btn btn-lg btn-cpp">
            <span>⚙️</span> C/C++分析
          </router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="visual-demo">
          <div class="demo-card">
            <div class="demo-header">变量赋值</div>
            <div class="demo-variables">
              <div class="demo-var">
                <span class="var-name">a</span>
                <span class="var-value">10</span>
              </div>
              <div class="demo-arrow">→</div>
              <div class="demo-var">
                <span class="var-name">b</span>
                <span class="var-value">20</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card" v-for="feature in features" :key="feature.title">
          <div class="feature-icon">{{ feature.icon }}</div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
          <router-link :to="feature.link" class="feature-link">
            了解更多 →
          </router-link>
        </div>
      </div>
    </section>

    <section class="examples-section">
      <div class="section-header">
        <h2 class="section-title">可视化示例</h2>
        <router-link to="/examples" class="btn btn-outline">查看全部示例</router-link>
      </div>
      <div class="examples-grid">
        <div class="example-card" v-for="example in examples" :key="example.title" @click="goToExample(example.path)">
          <div class="example-icon">{{ example.icon }}</div>
          <h3 class="example-title">{{ example.title }}</h3>
          <p class="example-description">{{ example.description }}</p>
          <div class="example-tags">
            <span class="badge" :class="example.language === 'Python' ? 'badge-python' : 'badge-cpp'">
              {{ example.language }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <section class="quick-start-section">
      <div class="quick-start-card">
        <h2 class="quick-start-title">快速开始</h2>
        <div class="quick-start-steps">
          <div class="step" v-for="step in quickStartSteps" :key="step.number">
            <div class="step-number">{{ step.number }}</div>
            <div class="step-content">
              <h4>{{ step.title }}</h4>
              <p>{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <footer class="footer">
      <div class="footer-content">
        <div class="footer-left">
          <div class="footer-logo">
            <span>📊</span>
            <span>CodeVis</span>
          </div>
          <p class="footer-description">代码可视化分析平台 - 让编程学习更直观</p>
        </div>
        <div class="footer-links">
          <div class="footer-link-group">
            <h4>快速链接</h4>
            <a href="/">首页</a>
            <a href="/python">Python分析</a>
            <a href="/c">C/C++分析</a>
            <a href="/examples">可视化示例</a>
          </div>
          <div class="footer-link-group">
            <h4>帮助支持</h4>
            <a href="#">使用教程</a>
            <a href="#">常见问题</a>
            <a href="#">更新日志</a>
            <a href="#">联系我们</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2024 CodeVis. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
const features = [
  {
    icon: '🐍',
    title: 'Python代码分析',
    description: '支持Python代码的语法解析、变量追踪和内存可视化，帮助理解代码执行过程。',
    link: '/python'
  },
  {
    icon: '⚙️',
    title: 'C/C++代码分析',
    description: '解析C/C++代码，模拟内存布局，展示指针操作和数组结构的可视化。',
    link: '/c'
  },
  {
    icon: '📊',
    title: '变量可视化',
    description: '直观展示变量的赋值过程、内存地址、值变化和引用关系。',
    link: '/examples'
  },
  {
    icon: '🔗',
    title: '拷贝对比',
    description: '对比原始对象、浅拷贝和深拷贝的内存布局，理解引用与独立对象的区别。',
    link: '/examples'
  },
  {
    icon: '📁',
    title: '文件管理',
    description: '上传、保存和管理代码文件，支持历史分析记录的保存和查看。',
    link: '/files'
  },
  {
    icon: '🔄',
    title: '单步执行',
    description: '支持代码的单步执行，逐步观察每一步的内存状态变化。',
    link: '/python'
  }
]

const examples = [
  {
    icon: '📦',
    title: '变量赋值',
    description: '查看变量的创建和赋值过程，追踪内存地址变化。',
    language: 'Python',
    path: '/python?example=variables'
  },
  {
    icon: '📋',
    title: '列表操作',
    description: '可视化列表的创建、修改和元素访问过程。',
    language: 'Python',
    path: '/python?example=list'
  },
  {
    icon: '🔗',
    title: '拷贝对比',
    description: '对比浅拷贝和深拷贝的内存布局差异。',
    language: 'Python',
    path: '/python?example=copy'
  },
  {
    icon: '📐',
    title: '二维数组',
    description: '展示二维数组的内存布局和元素访问。',
    language: 'C/C++',
    path: '/c?example=array'
  },
  {
    icon: '📍',
    title: '指针操作',
    description: '可视化指针的声明、赋值和指向关系。',
    language: 'C/C++',
    path: '/c?example=pointer'
  },
  {
    icon: '💾',
    title: '动态内存',
    description: '展示malloc和free的内存分配过程。',
    language: 'C/C++',
    path: '/c?example=malloc'
  }
]

const quickStartSteps = [
  {
    number: '01',
    title: '注册账户',
    description: '创建账户以保存分析记录和文件。'
  },
  {
    number: '02',
    title: '选择语言',
    description: '选择Python或C/C++进行代码分析。'
  },
  {
    number: '03',
    title: '输入代码',
    description: '编写或上传代码，选择示例模板。'
  },
  {
    number: '04',
    title: '运行分析',
    description: '点击运行，查看可视化效果。'
  }
]

const goToExample = (path) => {
  window.location.href = path
}
</script>

<style scoped>
.home-page {
  min-height: 100%;
}

.hero-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 80px 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.hero-content {
  flex: 1;
  max-width: 600px;
}

.hero-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.2;
}

.hero-description {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 32px;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 16px;
}

.hero-visual {
  flex: 1;
  display: flex;
  justify-content: center;
}

.visual-demo {
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-lg);
  padding: 32px;
}

.demo-card {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
  padding: 24px;
}

.demo-header {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 16px;
}

.demo-variables {
  display: flex;
  align-items: center;
  gap: 16px;
}

.demo-var {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: white;
  color: var(--primary-color);
  padding: 12px 20px;
  border-radius: var(--radius-md);
}

.var-name {
  font-size: 12px;
  color: var(--text-secondary);
}

.var-value {
  font-size: 20px;
  font-weight: 700;
}

.demo-arrow {
  font-size: 24px;
  font-weight: 300;
}

.features-section {
  padding: 60px 40px;
}

.section-title {
  font-size: 28px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 40px;
  color: var(--primary-color);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background-color: white;
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 12px;
}

.feature-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 16px;
}

.feature-link {
  display: inline-flex;
  align-items: center;
  color: var(--python-blue);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
}

.feature-link:hover {
  color: #2d6aa0;
}

.examples-section {
  padding: 60px 40px;
  background-color: var(--background-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto 40px;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.example-card {
  background-color: white;
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.3s ease;
}

.example-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--python-blue);
}

.example-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.example-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.example-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
}

.example-tags {
  display: flex;
  gap: 8px;
}

.quick-start-section {
  padding: 60px 40px;
}

.quick-start-card {
  max-width: 800px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius-lg);
  padding: 40px;
  color: white;
}

.quick-start-title {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 32px;
}

.quick-start-steps {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.step {
  display: flex;
  gap: 16px;
}

.step-number {
  font-size: 28px;
  font-weight: 700;
  opacity: 0.5;
  min-width: 40px;
}

.step-content h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.step-content p {
  font-size: 14px;
  opacity: 0.8;
}

.footer {
  background-color: var(--primary-color);
  color: white;
  padding: 40px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
}

.footer-left {
  flex: 1;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
}

.footer-description {
  font-size: 14px;
  opacity: 0.7;
}

.footer-links {
  display: flex;
  gap: 60px;
}

.footer-link-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-link-group h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.footer-link-group a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s ease;
}

.footer-link-group a:hover {
  color: white;
}

.footer-bottom {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 13px;
  opacity: 0.6;
}

@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
    gap: 40px;
  }
  
  .hero-title {
    font-size: 32px;
  }
  
  .hero-buttons {
    justify-content: center;
  }
  
  .quick-start-steps {
    grid-template-columns: 1fr;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 32px;
  }
}
</style>
