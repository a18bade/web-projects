// Import the functions you need from the SDKs you need
import firebase from "firebase/app";
import "firebase/auth";
import "firebase/firestore";


// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDBXAg-MeHxqNcTBWt4c9O0fVqISg8RQmo",
  authDomain: "authexample-4a2cc.firebaseapp.com",
  projectId: "authexample-4a2cc",
  storageBucket: "authexample-4a2cc.appspot.com",
  messagingSenderId: "344349062756",
  appId: "1:344349062756:web:680612edab1e23dec0d171",
  measurementId: "G-RWXG1QL07T"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// initalize components
export const auth = firebase.auth();
export const provider = new firebase.auth.GoogleAuthProvider();

export const db = firebase.firestore();
