<template>
  <div class="center">
  <h1> Done List </h1>
  <done-list></done-list>
  </div>
</template>

<script>
import { auth } from "@/firebaseConfig";
import DoneList from '@/components/DoneList.vue';
export default {
  components: { DoneList },
  name: 'DoneView',
  data: function() {
    return {
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
  methods: {
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