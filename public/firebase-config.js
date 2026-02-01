// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyDp5sa5XCPysutqQAIU2zHfIsnksIOOL7s",
    authDomain: "the-terrarium-c2070.firebaseapp.com",
    databaseURL: "https://the-terrarium-c2070-default-rtdb.europe-west1.firebasedatabase.app",
    projectId: "the-terrarium-c2070",
    storageBucket: "the-terrarium-c2070.firebasestorage.app",
    messagingSenderId: "108477557664",
    appId: "1:108477557664:web:55d392d47c05843f980c39"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Get database reference
const database = firebase.database();
