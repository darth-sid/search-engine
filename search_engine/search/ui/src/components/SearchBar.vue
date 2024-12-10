<script setup lang="ts">
import { ref } from 'vue'
import { nextTick } from 'vue'
import axios from 'axios'

const input = ref("")
const curr = ref("")
const retrieval_time = ref(0)
const results: Array = ref([])
const results_container = ref(null);

async function search(query: str) {
    const req = `//localhost:8000/search?query=${query}`
    const resp = await axios.get(req)
    return [resp.data["urls"], resp.data["time"]]
}

async function handleSearch(event) {
    const [new_results, time] = await search(event.target.value)
    retrieval_time.value = Math.trunc(time * 10**4) / 10**4
    results.value = new_results
    curr.value = input.value
    input.value = ""
    nextTick(() => {
        results_container.value.scrollTop = 0
    })
}
</script>

<template>
    <div class=search-container>
        <h1 class="search-title"> Search :D </h1>
        <input type=text
               class=search-bar
               placeholder=Search...
               v-model=input
               @keyup.enter=handleSearch
            />
        <p v-if="retrieval_time!=0" class=caption>{{!results.length ? 'No' : ''}} Search Results for "{{curr}}" ({{retrieval_time}}s)</p>
    </div>
    <div class=results-container ref="results_container">
        <ul v-if=results.length class=result_list>
            <li v-for="result in results" :key=result class=result>
                <a :href=result target=_blank class=result-link> {{result}} </a>
            </li>
        </ul>
    </div>
</template>

<style scoped>
.search-title {
    padding: 25px;
    margin: 0;
}
.search-container {
    width: 80vw;
    background-color: rgb(36,36,36);
    min-height: 190px;
    max-height: 25vh;
    position: sticky;
    top: 0px;
    padding: 0;
    max-width: 100%;
    box-shadow: rgb(36,36,36) 0px 10px 10px 10px;
    white-space: nowrap;
}
.results-container {
    width: 80vw;
    background-color: #242424;
    max-height: 75vh;
    overflow-y: auto;
    min-height: 30vh;
    text-align: left;
}
.search-bar {
    height: 50px;
    border-radius: 25px;
    background-color: #363636;
    padding: 5px 25px;
    box-sizing: border-box;
    width: 100%;
    border-style: solid;
}
.caption {
    color: #808080;
}
.result_list {
    list-style-type: none;
}
.result{
    padding-bottom: 10px;
}
.result-link {
    display: inline-block;
    width: 100%;
    overflow-x: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    
}
</style>
