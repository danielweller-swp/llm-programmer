<script setup lang="ts">
import { computed, ref } from 'vue'
import axios from 'axios'

const taskDescription = ref<string>(`Create a program that prints the first n primes.`)

type Status = "waiting" | "working" | "done"

const requirementSubmitted = ref<boolean>(false)
const taskDone = computed<boolean>(() => logs.value.length > 0 && logs.value[logs.value.length-1].type === 'end')

const status = computed<Status>(() => {
  if (requirementSubmitted.value) {
    if (taskDone.value) {
      return "done"
    } else {
      return "working"
    }
  } else {
    return "waiting"
  }
})

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
const baseUrl = 'http://localhost:8000'

const checkLogs = () => {
  axios
    .get(`${baseUrl}/log`)
    .then(response => {
      console.log(response.data)
      logs.value = response.data
      if (!taskDone.value) {
        setTimeout(checkLogs, 1000)
      }
    })
}

const submitRequirement = () => {
  requirementSubmitted.value = true
  console.log({ description: taskDescription.value })
  axios
    .post(`${baseUrl}/task`, { description: taskDescription.value })
    .then(response => {
      console.log(response.data)
      checkLogs()
    })
}

const diffUrl = computed<string>(() => taskDone.value ? `${baseUrl}/diff` : 'about:blank')

const commitMsg = ref<string>("")

const reset = () => {
  requirementSubmitted.value = false
  logs.value = []
}

const commit = () => {
  axios
    .post(`${baseUrl}/commit`, { msg: commitMsg.value })
    .then(response => {
      console.log("Commit successful")
      reset()
    })
}

const revert = () => {
  axios
    .post(`${baseUrl}/revert`)
    .then(response => {
      console.log("Revert successful")
      reset()
    })
}
</script>

<template>
  <div v-if="status === 'waiting'">
    Task:<br/>
    <textarea v-model="taskDescription" class="task-description"></textarea><br/>
    <button @click="submitRequirement()">Go!</button><br/>
  </div>
  <div v-if="status === 'working' || status === 'done'">
    Task: {{ taskDescription }}<br/>
    <i>Working...</i><br/>
    <div v-for="item in logs" class="log-item">
      <span v-if="item.type === 'action'">
        <span v-if="item.msg && item.msg != ''"><i>Thought: </i>{{ item.msg }}<br/></span>
        <i>Action: </i>
          <span v-if="item.tool === 'write_file'">Wrote file <span class="code-inline">{{  item.tool_input.file_path }}</span>.</span>
          <span v-if="item.tool === 'read_file'">Read file <span class="code-inline">{{  item.tool_input.file_path }}</span>.</span>
          <span v-if="item.tool === 'execute_bash'">Executed bash:<br/><span class="code-inline">{{  item.tool_input.cmd }}</span>.</span>
      </span>
      <span v-if="item.type === 'end'">
        <span v-if="item.msg && item.msg != ''"><i>Thought: </i>{{ item.msg }}<br/></span>
        <i>Done!</i>
      </span>
    </div>
    <div v-if="status === 'done'">
      <iframe :src="diffUrl" width="100%" height="500px"></iframe>
      <input type="text" v-model="commitMsg"/>
      <button @click="commit">Commit!</button>
      <button @click="revert">Revert</button>
    </div>
  </div>
</template>

<style scoped>
.task-description {
  width: 500px;
  height: 500px;
}

.log-item {
  border: 1px solid black;
  margin: 10px;
}

.code-inline {
  font-family: 'Lucida Console', monospace;
}
</style>
