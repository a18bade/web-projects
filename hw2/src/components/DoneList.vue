<template>
<div>
  <ul v-if="todos!=false" style="list-style: none;">
    <li v-for="todo in todos" :key="todo.id">
      <div v-if="todo.isDone === true && todo.task_creator === user.email ">
        <span id ="task">{{todo.task}}</span>
        <input type="button" value="not done" @click="updateTask(todo.id,false)">
      </div>
    </li>
  </ul>
</div>
</template>

<script>
import { auth } from "@/firebaseConfig";
import { db } from '@/firebaseConfig'
export default {
  name: 'DoneList',
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
        this.$router.push({path: '/'});
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
