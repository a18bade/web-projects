<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/todos">Todo</router-link>|
      <router-link to="/done">Done</router-link>
    <login-button/>
    </nav>
    <router-view/>
  </div>
</template>

<script>
import { auth } from "@/firebaseConfig";

import LoginButton from './components/LoginButton.vue'
export default {
  components: { LoginButton },
  beforeCreate: function() {

    auth.getRedirectResult().then(result=>{
      if (result.user) {
        this.$router.push("/todos")
      }
    }).catch(() => {
      this.$router.push("/itsAllForNothing")
    })
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  
  color: #2c3e50;
}

nav {
  text-align: center;
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}

body {
  background-color: rgb(214, 84, 36);
}
</style>
