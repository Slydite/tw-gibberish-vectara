// src/components/InputView.vue
<template>
  <div class="input-view">
    <div class="model-header">
      <h1>Model Input</h1>
    </div>

    <div class="input-container">
      <div class="input-section">
        <h2>Gibberish Model</h2>
        <div class="input-group">
          <label for="gibberish-input">Input Text:</label>
          <textarea id="gibberish-input" v-model="gibberishInput" placeholder="Enter text for Gibberish detection"></textarea>
        </div>
        <button @click="predictGibberish" class="predict-btn">Predict Gibberish</button>
      </div>

      <div class="input-section">
        <h2>Vectara Model</h2>
        <div class="input-group">
          <label for="vectara-input1">Input 1:</label>
          <textarea id="vectara-input1" v-model="vectaraInput1" placeholder="Enter input 1 for Vectara"></textarea>
        </div>
        <div class="input-group">
          <label for="vectara-input2">Input 2:</label>
          <textarea id="vectara-input2" v-model="vectaraInput2" placeholder="Enter input 2 for Vectara"></textarea>
        </div>
        <button @click="predictVectara" class="predict-btn">Predict Vectara</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'InputView',
  setup() {
    const gibberishInput = ref('');
    const vectaraInput1 = ref('');
    const vectaraInput2 = ref('');

    const predictGibberish = async () => {
      try {
        
        console.log(gibberishInput.value)
        const response = await axios.post('http://localhost:8000/api/predict/gibberish', {
          input_text: gibberishInput.value
        });
        
        console.log('Gibberish Prediction Response:', response.data);
        alert('Gibberish Prediction Success! Check console for details.'); 
        gibberishInput.value = ''; 
      } catch (error) {
       
  
        console.error('Error predicting Gibberish:', error);
        alert('Gibberish Prediction Failed! Check console for errors.'); 
      }
    };

    const predictVectara = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/predict/vectara', {
          input_1: vectaraInput1.value,
          input_2: vectaraInput2.value
        });
        console.log('Vectara Prediction Response:', response.data);
        alert('Vectara Prediction Success! Check console for details.');
        vectaraInput1.value = ''; 
        vectaraInput2.value = '';
      } catch (error) {
        console.error('Error predicting Vectara:', error);
        alert('Vectara Prediction Failed! Check console for errors.'); 
      }
    };

    return {
      gibberishInput,
      vectaraInput1,
      vectaraInput2,
      predictGibberish,
      predictVectara,
    };
  },
});
</script>

<style scoped>
.input-view {
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

.input-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  background-color: transparent; 
}

@media (max-width: 768px) {
  .input-container {
    grid-template-columns: 1fr;
  }
}

.input-section {
  border-radius: 8px;
  padding: 1.5rem;
  background-color: transparent; 
}

.input-section h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: var(--color-text);
}

.input-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1.5rem;
}

.input-group label {
  margin-bottom: 0.5rem;
  color: var(--color-text);
  font-weight: bold;
}

.input-group textarea {
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid var(--color-table-border);
  background-color: #141516; 
  color: var(--color-text);
  font-family: inherit;
  font-size: 1rem;
  min-height: 100px;
  resize: vertical;
}

.predict-btn {
  background-color: var(--color-button);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 1rem;
  border: 1px solid #736b5e; 
}

.predict-btn:hover {
  background-color: var(--color-button-hover);
  border-color: #3391ff; 
}
</style>