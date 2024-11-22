<script setup lang="ts">
//import {PyBridge} from 'pybridge'
import { ref } from 'vue'

function search() {
    console.log("Search!")
}

const input = ref("")
const results = ref(["Hello"])
results.push("Hola")

</script>

<template>
    <div class="search-container">
        <input type="text"
               class="search-bar"
               placeholder="Search..."
               v-model="input"
               @input="search"
            />
        <p> {{results.length}} </p>
        <ul v-if="results.length">
            <li v-for="result in results" :key="result">
                {{result}}
            </li>
        </ul>
    </div>
</template>

<style scoped>
.search-container {
    width: 100%;
    background-color: #242424;
    height: 100%;
}
.search-bar {
    height: 50px;
    border-radius: 25px;
    background-color: #363636;
    padding: 5px 25px;
    box-sizing: border-box;
    width: 100%;
}
</style>
