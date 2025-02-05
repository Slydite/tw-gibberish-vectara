<template>
  <div class="model">
    <div class="model-header">
      <h1>Evaluation Results - {{ modelType }}</h1>
      <div class="controls">
        <button @click="fetchModelData" class="refresh-btn">
          Refresh Data
        </button>
        <label class="auto-refresh">
          <input type="checkbox" v-model="autoRefreshEnabled" @change="toggleAutoRefresh">
          Auto-refresh
        </label>
      </div>
    </div>

    <div class="metrics-summary">
      <StatsCard
        v-if="modelType === 'Vectara'"
        :stats="vectaraStats"
      />
    </div>

    <div class="charts-container">
      <template v-if="modelType === 'Vectara'">
        <div class="chart-wrapper">
          <div id="timeSeriesChart"></div> 
        </div>
        <div class="chart-wrapper">
          <div id="distributionChart"></div>
        </div>
        <div class="chart-wrapper">
          <div id="processingTimeChart"></div>
        </div>
      </template>
      <template v-if="modelType === 'Gibberish'">
        <div class="chart-wrapper">
          <div id="cleanProbChart"></div>
        </div>
        <div class="chart-wrapper">
          <div id="mildGibberishChart"></div>
        </div>
        <div class="chart-wrapper">
          <div id="noiseChart"></div>
        </div>
        <div class="chart-wrapper">
          <div id="wordSaladChart"></div>
        </div>
        <div class="chart-wrapper">
          <div id="labelDistributionChart"></div>
        </div>
        <div class="chart-wrapper">
          <div id="processingTimeChart"></div>
        </div>
      </template>
    </div>

    <div class="model-table">
      <table>
        <thead>
          <tr>
            <th>Prediction ID</th>
            <th v-if="modelType === 'Vectara'">Input 1</th>
            <th v-if="modelType === 'Vectara'">Input 2</th>
            <th v-if="modelType === 'Vectara'">Score</th>
            <th v-if="modelType === 'Gibberish'">Input Text</th>
            <th v-if="modelType === 'Gibberish'">Label</th>
            <th v-if="modelType === 'Gibberish'">Prob. Clean</th>
            <th v-if="modelType === 'Gibberish'">Prob. Mild Gibberish</th>
            <th v-if="modelType === 'Gibberish'">Prob. Noise</th>
            <th v-if="modelType === 'Gibberish'">Prob. Word Salad</th>
            <th>Timestamp</th>
            <th>Processing Time (ms)</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="data in recentModelData" :key="data.prediction_id">
            <td>{{ data.prediction_id }}</td>
            <template v-if="modelType === 'Vectara' && isVectaraResult(data)">
              <td>{{ truncateText(data.input_1) }}</td>
              <td>{{ truncateText(data.input_2) }}</td>
              <td>{{ formatNumber(data.output_score) }}</td>
            </template>
            <template v-if="modelType === 'Gibberish' && isGibberishResult(data)">
              <td>{{ truncateText(data.input_text) }}</td>
              <td>{{ data.predicted_label }}</td>
              <td>{{ formatNumber(data.prob_clean) }}</td>
              <td>{{ formatNumber(data.prob_mild_gibberish) }}</td>
              <td>{{ formatNumber(data.prob_noise) }}</td>
              <td>{{ formatNumber(data.prob_word_salad) }}</td>
            </template>
            <td>{{ formatDate(data.timestamp) }}</td>
            <td>{{ data.processing_time_ms }}ms</td>
            <td>
              <span :class="['status', data.status]">{{ data.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted, watch, type Ref, nextTick } from 'vue'
import { format } from 'date-fns'
import axios from 'axios'
import ApexCharts from 'apexcharts'
import StatsCard from './StatsCard.vue'
import { VectaraResult, GibberishResult } from '@/types'
import { initializeCharts, updateCharts } from '@/utils/charts'
import { calculateStats } from '@/utils/stats'

export default defineComponent({
  name: 'ModelView',
  components: {
    StatsCard
  },
  props: {
    modelType: {
      type: String,
      required: true,
      validator: (value: string) => ['Vectara', 'Gibberish'].includes(value)
    }
  },
  setup(props: { modelType: string }) {
    const modelResults: Ref<VectaraResult[] | GibberishResult[] | null> = ref(null)
    const charts: Ref<{
      timeSeries: ApexCharts | null,
      distribution: ApexCharts | null,
      cleanProb: ApexCharts | null,
      mildGibberish: ApexCharts | null,
      noise: ApexCharts | null,
      wordSalad: ApexCharts | null,
      labelDistribution: ApexCharts | null,
      processingTime: ApexCharts | null
    }> = ref({
      timeSeries: null,
      distribution: null,
      cleanProb: null,
      mildGibberish: null,
      noise: null,
      wordSalad: null,
      labelDistribution: null,
      processingTime: null
    })
    const autoRefreshEnabled = ref(true)
    const refreshInterval = ref<NodeJS.Timeout>()

    const chartsInitialized = ref(false)

    const recentModelData = computed(() => modelResults.value || [])

    const vectaraStats = computed(() => {
      if (!modelResults.value || props.modelType !== 'Vectara') return {}; 
      return calculateStats(modelResults.value as VectaraResult[]);
    })

    const gibberishStats = computed(() => {
      if (!modelResults.value || props.modelType !== 'Gibberish') return {}; 
      return calculateStats(modelResults.value as GibberishResult[]);
    })

    watch(
      () => props.modelType,
      async (newType: string) => {
        console.log('Model type changed to:', newType);
        if (chartsInitialized.value) {
          Object.values(charts.value).forEach(chart => {
            if (chart) {
              chart.destroy();
            }
          });
          charts.value = {
            timeSeries: null,
            distribution: null,
            cleanProb: null,
            mildGibberish: null,
            noise: null,
            wordSalad: null,
            labelDistribution: null,
            processingTime: null
          };
          chartsInitialized.value = false;
        }

        await initializeChartsForType(newType);

        fetchModelData();
      }
    );

    const initializeChartsForType = async (modelType: string) => {
      const chartOptions = initializeCharts();
      
      await nextTick();

      if (modelType === 'Vectara') {
        const timeSeriesElement = document.querySelector('#timeSeriesChart');
        const distributionElement = document.querySelector('#distributionChart');
        const processingTimeElement = document.querySelector('#processingTimeChart');
        
        if (timeSeriesElement && distributionElement && processingTimeElement) {
          charts.value.timeSeries = new ApexCharts(timeSeriesElement, chartOptions.timeSeries);
          charts.value.distribution = new ApexCharts(distributionElement, chartOptions.distribution);
          charts.value.processingTime = new ApexCharts(processingTimeElement, chartOptions.processingTime);
          
          await Promise.all([
            charts.value.timeSeries.render(),
            charts.value.distribution.render(),
            charts.value.processingTime.render()
          ]);
        }
      } else {
        const cleanProbElement = document.querySelector('#cleanProbChart');
        const mildGibberishElement = document.querySelector('#mildGibberishChart');
        const noiseElement = document.querySelector('#noiseChart');
        const wordSaladElement = document.querySelector('#wordSaladChart');
        const labelDistElement = document.querySelector('#labelDistributionChart');
        const processingTimeElement = document.querySelector('#processingTimeChart');

        if (cleanProbElement && mildGibberishElement && noiseElement && 
            wordSaladElement && labelDistElement && processingTimeElement) {
          charts.value.cleanProb = new ApexCharts(cleanProbElement, chartOptions.cleanProb);
          charts.value.mildGibberish = new ApexCharts(mildGibberishElement, chartOptions.mildGibberish);
          charts.value.noise = new ApexCharts(noiseElement, chartOptions.noise);
          charts.value.wordSalad = new ApexCharts(wordSaladElement, chartOptions.wordSalad);
          charts.value.labelDistribution = new ApexCharts(labelDistElement, chartOptions.labelDistribution);
          charts.value.processingTime = new ApexCharts(processingTimeElement, chartOptions.processingTime);

          await Promise.all([
            charts.value.cleanProb.render(),
            charts.value.mildGibberish.render(),
            charts.value.noise.render(),
            charts.value.wordSalad.render(),
            charts.value.labelDistribution.render(),
            charts.value.processingTime.render()
          ]);
        }
      }
      chartsInitialized.value = true;
    };

    const fetchModelData = async () => {
      try {
        const url = `http://localhost:8000/api/results/${props.modelType.toLowerCase()}`
        const response = await axios.get(url)
        modelResults.value = response.data.map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }))

        if (chartsInitialized.value && modelResults.value && modelResults.value.length > 0) {
          updateCharts(charts.value, modelResults.value, props.modelType);
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }

    const toggleAutoRefresh = () => {
      if (autoRefreshEnabled.value) {
        refreshInterval.value = setInterval(fetchModelData, 10000)
      } else {
        if (refreshInterval.value) {
          clearInterval(refreshInterval.value)
        }
      }
    }

    const truncateText = (text: string, length = 50) => {
      return text.length > length ? `${text.substring(0, length)}...` : text
    }

    const formatNumber = (num: number) => {
      return num.toFixed(4)
    }

    const formatDate = (date: Date) => {
      return format(date, 'yyyy-MM-dd HH:mm:ss')
    }

    const isVectaraResult = (data: any): data is VectaraResult => {
      return 'input_1' in data && 'input_2' in data && 'output_score' in data
    }

    const isGibberishResult = (data: any): data is GibberishResult => {
      return 'input_text' in data && 'predicted_label' in data && 'prob_clean' in data
    }

    onMounted(async () => {
      await initializeChartsForType(props.modelType);
      fetchModelData();
      if (autoRefreshEnabled.value) {
        toggleAutoRefresh();
      }
    });

    onUnmounted(() => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value);
      }
      Object.values(charts.value).forEach(chart => {
        if (chart) {
          chart.destroy();
        }
      });
      chartsInitialized.value = false;
    });

    return {
      recentModelData,
      vectaraStats,
      gibberishStats,
      autoRefreshEnabled,
      fetchModelData,
      toggleAutoRefresh,
      truncateText,
      formatNumber,
      formatDate,
      isVectaraResult,
      isGibberishResult,
      charts 
    }
  }
})
</script>
<style scoped>
.model {
  padding: 1rem;
  background-color: transparent;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  color: #ffffff;
}

.controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.refresh-btn {
  background-color: var(--color-button);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid #736b5e;
}

.refresh-btn:hover {
  background-color: var(--color-button-hover);
  border-color: #3391ff;
}

.metrics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.chart-wrapper {
  border-radius: 8px;
  padding: 1rem;
  background-color: transparent;
}

.model-table {
  overflow-x: auto;
  background-color: transparent;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th,
td {
  border: 1px solid var(--color-table-border);
  padding: 0.75rem;
  text-align: left;
  color: #ffffff;
}

th {
  background-color: var(--color-table-header); 
  color: white;
  font-weight: 500;
}

td {
  background-color: transparent; 
}


.status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.status.success {
  background-color: rgba(37, 163, 90, 0.2); 
  color: #47d583;
}

.status.error {
  background-color: rgba(162, 33, 20, 0.2); 
  color: #e95849;
}

@media (max-width: 1024px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .model-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .metrics-summary {
    grid-template-columns: 1fr;
  }
}
</style>