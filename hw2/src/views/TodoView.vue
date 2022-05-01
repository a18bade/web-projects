<template>
  <div class="center">
  <h1> Tasks TODO</h1>
  <input v-model="newTodo" placeholder="description of task" @keyup.enter="addNewTask" />
  <button @click="addNewTask">+</button>
  <todo-list></todo-list>
  </div>
</template>

<script>
import { auth } from "@/firebaseConfig";
import { db } from '@/firebaseConfig'
import TodoList from '@/components/TodoList.vue';
export default {
  components: { TodoList },
  name: 'TodoView',
  data: function() {
    return {
      newTodo: "",
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
  methods: {
    addNewTask: function() {
      let newTodo = {
        task: this.newTodo,
        isDone:false,
        task_creator: this.user.email,
        created_at: Date.now()

      };
      this.newTodo = ""
      db.collection("todoCollection").add(newTodo)
    }
  }
}
</script>

<style scoped>
.center {
  margin-left: auto;
  margin-right: auto;
  text-align: center;
}
</style>