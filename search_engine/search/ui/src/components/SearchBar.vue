<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const input = ref("")
const curr = ref("")
const retrieval_time = ref(0)
const results: Array = ref([])

async function search(query: str) {
    const req = `//localhost:8000/search?query=${query}`
    const resp = await axios.get(req)
    return [resp.data["urls"], resp.data["time"]]
}

async function handleSearch(event) {
    const [new_results, time] = await search(event.target.value)
    retrieval_time.value = Math.trunc(time * 10**4) / 10**4
    console.log(new_results)
    console.log(time)
    results.value = new_results
    curr.value = input.value
    input.value = ""
}
</script>

<template>
    <div class=search-container>
        <input type=text
               class=search-bar
               placeholder=Search...
               v-model=input
               @keyup.enter=handleSearch
            />
        <p v-if=results.length class=caption> Search Results for "{{curr}}" ({{retrieval_time}}s)</p>
        <ul v-if=results.length class=result_list>
            <li v-for="result in results" :key=result class=result>
                <a :href=result target=_blank> {{result}} </a>
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
.caption {
    color: #808080;
}
.result_list {
    list-style-type: none;
}
.result{
    padding-bottom: 10px;
};
</style>
