// backend/seed.js
const mongoose = require('mongoose');
const Course = require('./models/Course');
require('dotenv').config();

const courses = [
  {
    courseCode: "UE25CS3501",
    courseTitle: "Deep Learning",
    credits: 3,
    ltp: "3-0-0",
    hoursPerWeek: 3,
    aims: "This course introduces students to the principles and applications of Deep Learning, focusing on mathematical foundations, neural network architectures, and optimization techniques.",
    objectives: [
      "To introduce students to the fundamentals of AI, ML, and Deep Learning.",
      "To understand the mathematical foundations of neural networks.",
      "To explain the architecture of feedforward networks.",
      "To provide knowledge of optimization algorithms.",
      "To develop skills in CNN implementation.",
      "To understand RNNs and sequence modeling.",
      "To explore generative models like GANs.",
      "To discuss ethical AI concepts.",
      "To analyze real-world applications of DL.",
      "To prepare students for advanced AI research."
    ],
    outcomes: [
      { code: "CO1", description: "Recall the concepts of AI, ML, and Deep Learning fundamentals." },
      { code: "CO2", description: "Explain activation functions and backpropagation algorithms." },
      { code: "CO3", description: "Apply CNNs for image classification tasks." },
      { code: "CO4", description: "Analyze sequence data using RNNs and LSTMs." },
      { code: "CO5", description: "Evaluate models using optimization techniques." },
      { code: "CO6", description: "Design real-world deep learning solutions." }
    ],
    syllabusUnits: [
      { unitNumber: "I", title: "INTRODUCTION TO DEEP LEARNING", topics: ["Fundamentals of AI", "History", "Perceptron", "Activation Functions"] },
      { unitNumber: "II", title: "NETWORK TRAINING", topics: ["Epochs", "Learning Rate", "Optimization", "Regularization"] },
      { unitNumber: "III", title: "CNN", topics: ["Convolution Layers", "Pooling", "CNN Architectures"] },
      { unitNumber: "IV", title: "RNN AND NLP", topics: ["Sequence Modeling", "LSTM", "Attention Mechanism"] },
      { unitNumber: "V", title: "ADVANCED TOPICS", topics: ["Autoencoders", "GANs", "Explainable AI"] }
    ],
    assessment: { quiz: 15, test: 25, assignment: 20, see: 40, total: 100 },
    textbooks: ["Ian Goodfellow - Deep Learning", "Francois Chollet - DL with Python"],
    grading: [
      { range: "91+", grade: "O", description: "Outstanding" },
      { range: "81-90", grade: "A+", description: "Excellent" }
    ]
  },
  {
    courseCode: "UE25CS3502",
    courseTitle: "AR/VR and Metaverse Technologies",
    credits: 3,
    ltp: "3-0-0",
    hoursPerWeek: 3,
    aims: "This course introduces students to the rapidly evolving fields of Augmented Reality (AR), Virtual Reality (VR), and the emerging Metaverse.",
    objectives: [
      "To provide a strong foundation in immersive technologies.",
      "To explain the evolution of AR and VR systems.",
      "To understand the hardware components of immersive systems.",
      "To introduce 3D mathematics and spatial computing.",
      "To develop skills in interactive 3D application design.",
      "To explore AR/VR interaction paradigms and user experience.",
      "To introduce the architecture and components of the Metaverse.",
      "To explain digital identity and virtual economies.",
      "To discuss interoperability and standards in immersive systems.",
      "To analyze ethical and societal implications of immersive technologies."
    ],
    outcomes: [
      { code: "CO1", description: "Recall the concepts, terminology, and historical evolution of AR, VR, MR, and the Metaverse." },
      { code: "CO2", description: "Explain the technical components and hardware requirements of AR/VR systems." },
      { code: "CO3", description: "Apply 3D mathematics and spatial computing principles for virtual object placement." },
      { code: "CO4", description: "Analyze user interaction paradigms and interface design in immersive environments." },
      { code: "CO5", description: "Evaluate development platforms, engines, and tools for creating immersive applications." },
      { code: "CO6", description: "Design and develop a functional AR or VR application using industry-standard tools." }
    ],
    syllabusUnits: [
      { 
        unitNumber: "I", 
        title: "FOUNDATIONS OF IMMERSIVE TECHNOLOGIES", 
        topics: ["Introduction to Immersive Technologies", "History and Evolution", "Virtual Reality Systems", "Augmented Reality Systems", "Metaverse Concepts and Definitions"] 
      },
      { 
        unitNumber: "II", 
        title: "HARDWARE AND RENDERING FOR IMMERSIVE SYSTEMS", 
        topics: ["Display Technologies (HMDs, HUDs)", "Tracking and Localization Systems", "SLAM and Spatial Awareness", "Immersive Rendering Pipeline"] 
      },
      { 
        unitNumber: "III", 
        title: "3D MATHEMATICS AND SPATIAL COMPUTING", 
        topics: ["Coordinate Systems and Transformations", "Quaternions and Rotations", "Camera Models and Projections", "Spatial Mapping and Meshing"] 
      },
      { 
        unitNumber: "IV", 
        title: "AR/VR DEVELOPMENT AND INTERACTION", 
        topics: ["Development Platforms (Unity, Unreal)", "Core Interactions (Gaze, Gesture, Voice)", "Spatial Audio and Haptics", "UX Design for XR"] 
      },
      { 
        unitNumber: "V", 
        title: "METAVERSE, ECONOMICS AND FUTURE DIRECTIONS", 
        topics: ["Metaverse Architecture and Layers", "Digital Identity and Avatars", "Virtual Economies and NFTs", "Ethics, Privacy and Societal Impact"] 
      }
    ],
    assessment: { quiz: 15, test: 25, assignment: 20, see: 40, total: 100 },
    textbooks: [
      "Schmalstieg, D., & Hollerer, T. (2016). Augmented Reality: Principles and Practice.",
      "LaValle, S. M. (2019). Virtual Reality. Cambridge University Press.",
      "Aukstakalnis, S. (2016). Practical Augmented Reality.",
      "Casey, K. (2022). The Metaverse: And How it Will Revolutionize Everything."
    ],
    grading: [
      { range: "91+", grade: "O", description: "Outstanding (91 and above)" },
      { range: "81-90", grade: "A+", description: "Excellent (81-90)" },
      { range: "71-80", grade: "A", description: "Very Good (71-80)" },
      { range: "61-70", grade: "B+", description: "Good (61-70)" },
      { range: "51-60", grade: "B", description: "Above Average (51-60)" },
      { range: "40-50", grade: "C", description: "Average (40-50)" },
      { range: "Below 40", grade: "D", description: "Not Satisfactory (Below 40)" }
    ]
  }
];

mongoose.connect(process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/course_search_engine')
  .then(async () => {
    console.log('MongoDB Connected');
    await Course.deleteMany({});
    console.log('Previous courses removed');
    await Course.insertMany(courses);
    console.log('Sample courses added including full AR/VR course');
    process.exit();
  })
  .catch(err => {
    console.error(err);
    process.exit(1);
  });
