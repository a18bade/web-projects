<template>
<div>
  <ul v-if="todos!=false" style="list-style: none;">
    <li v-for="todo in todos" :key="todo.id">
      <div v-if="todo.isDone === false && todo.task_creator === user.email ">
        <router-link id ="task" :to="{ name: 'todoID', params: { id: todo.id}}">{{todo.task}}</router-link>
        <input type="button" value=done @click="updateTask(todo.id,true)">
      </div>
    </li>
  </ul>
</div>
</template>

<script>
import { auth } from "@/firebaseConfig";
import { db } from '@/firebaseConfig'
export default {
  name: 'TodoList',
  props:{
  },
  data: function() {
    return {
      todos: false,
      user: null
    }
  },
  beforeCreate: function() {
    auth.onAuthStateChanged(user => {
      if (user) {        
        this.user = user;
      } else {
        this.user = null;
      }
    });
  },
  firestore: {
    todos: db.collection("todoCollection").orderBy("created_at","desc")
  },
  methods: {
    updateTask: function(id,completed) {
        db.collection("todoCollection").doc(id).update({isDone:completed})
    }
  }
}
</script>

<style scoped>
#task {
    padding-right: 2px;
}
</style>