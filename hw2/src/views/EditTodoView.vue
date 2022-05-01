<template>
  <div v-if="todo !== false">
    <h1>Task: {{todo.task}}</h1>
    <br>
    <textarea @keyup.enter="updateTask" v-model="todo.task"/>
    <br>
    <button @click="updateTask">Save</button>
    <br>
    <button @click="doneTask">Done</button>
    

  </div>
</template>

<script>
import { auth } from "@/firebaseConfig";
import { db } from '@/firebaseConfig'
export default {
    data: function() {
        return {
            todo: false,
            id: this.$route.params.id
        }
    },
    firestore: function() {
        console.log("does this even run");
        console.log(this.id);
        return {
            todo: db.collection("todoCollection").doc(this.id)
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
        updateTask: function() {
            this.$firestoreRefs.todo.update({task:this.todo.task})
            console.log(this.$route.name)
            this.$router.push({name:'todos'})
        },
        doneTask: function() {
            this.$firestoreRefs.todo.update({isDone:true})
            this.$router.push({name:'todos'})
      }
    }
}
</script>