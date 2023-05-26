<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const taskDescription = ref<string>("Create an empty file called test.txt.")

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

type LogItem = ActionLogItem | EndLogItem

const logs = ref<LogItem[]>([])

const checkLogs = () => {
  console.log('checking logs')
  axios
    .get('http://127.0.0.1:8000/log')
    .then(response => {
      logs.value = response.data
      if (!(logs.value.length > 0 && logs.value[logs.value.length-1].type === 'end')) {
        setTimeout(checkLogs, 1000)
      }
    })
}

const submitTask = () => {
  logs.value = []
  console.log({ description: taskDescription.value })
  axios
    .post('http://127.0.0.1:8000/task', { description: taskDescription.value })
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
      <i>Thought: </i>{{ item.msg }}<br/>
      <i>Tool Used: </i>{{ item.tool }}
    </span>
    <span v-if="item.type === 'end'">
      <i>Thought: </i>{{ item.msg }}<br/>
      <i>I'm done!</i>
    </span>
        
    {{ item.type }}: {{ item.msg }}
  </div>
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
