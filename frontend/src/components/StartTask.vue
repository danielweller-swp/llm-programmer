<script setup lang="ts">
import { computed, ref } from 'vue'
import axios from 'axios'

const taskDescription = ref<string>(`Create a program that prints the first n primes.

Example output: 
\`\`\`
$ node primes.js 3
2, 3, 4
\`\`\``)

type GiveUpLogItem = {
  type: "give_up"
}

type ActionLogItem = {
  type: "action"
  msg: string
  tool: string
  tool_input: any
}

type EndLogItem = {
  type: "end"
  msg: string
  return_values: any
}

type LogItem = ActionLogItem | EndLogItem | GiveUpLogItem

const logs = ref<LogItem[]>([])
const baseUrl = 'http://localhost:8000'

const done = computed<boolean>(() => logs.value.length > 0 && logs.value[logs.value.length-1].type === 'end')

const checkLogs = () => {
  console.log('checking logs')
  axios
    .get(`${baseUrl}/log`)
    .then(response => {
      console.log(response.data)
      logs.value = response.data
      if (!done.value) {
        setTimeout(checkLogs, 1000)
      }
    })
}

const submitTask = () => {
  logs.value = []
  console.log({ description: taskDescription.value })
  axios
    .post(`${baseUrl}/task`, { description: taskDescription.value })
    .then(response => {
      console.log(response.data)
      checkLogs()
    })
}
</script>

<template>
  Task:<br/>
  <textarea v-model="taskDescription" class="taskDescription"></textarea><br/>
  <button @click="submitTask()">Go!</button><br/>
  Log:<br/>
  <div v-for="item in logs" class="logItem">
    <span v-if="item.type === 'action'">
      <span v-if="item.msg && item.msg != ''"><i>Thought: </i>{{ item.msg }}<br/></span>
      <i>Tool Used: </i>{{ item.tool }}
    </span>
    <span v-if="item.type === 'end'">
      <span v-if="item.msg && item.msg != ''"><i>Thought: </i>{{ item.msg }}<br/></span>
      <i>I'm done!</i>
    </span>
    <span v-if="item.type === 'give_up'">
      <i>I'm giving up and retrying.</i>
    </span>
  </div>
  <button :disabled="!done">View Diff</button>
</template>

<style scoped>
.taskDescription {
  width: 500px;
  height: 500px;
}

.logItem {
  border: 1px solid black;
  margin: 10px;
}
</style>
