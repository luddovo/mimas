# 🚀 mimas


### 🌟 Minimalist Mail System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

---

## 📖 Overview

**Mimas** 

Mimas is a minimalist mail system for accessing e-mails over extremely bandwidth-restricted connnections (50 bytes/second) with a CLI interface capable of running on almost any hardware with terminal support.
Targeted to be used over satellite and HF links from remote locations on basic hardware.

---

## 📜 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)

---

## ✨ Features
✅ Server-side script that communicates with Gmail API

✅ CLI Client to read, send and manage mail

✅ Extremely bandwidth-efficient communication (can work over SMS messages, HF links, satellite messages)

✅ All communication encoded in text-safe Base91 encoding

✅ Transcoding to minimal huffman-encoded charset - less than 5 bits per character on average

---

## 🔧 Installation
1. **Clone the repository**  
   ```sh
   git clone https://github.com/luddovo/mimas.git
   cd project


## 🚀 Usage

One possible usage scenario:

- Set-up the server component on a machine that can process incoming e-mails
- Install the client on your local machine
- Use Winlink to pass commands from client to server and get results
- 
