# 🔒 Java Application Blocker & Deadlock Tool

A **Java-based system blocker and productivity assistant** designed to help users manage their application usage through blocking mechanisms such as timers, daily limits, and password protection.

> **Status:** Some features are fully functional, others under development.

---

## 🧩 Project Structure

This Java application allows users to:

* ✅ **Create custom blocks** for selected applications.
* 🔐 **Restrict access** using:

  * Countdown timers
  * Delayed start blocking
  * Daily usage limits
  * Password locks
* 🚫 **Create deadlocks** that are more strict and harder to bypass.
* 🛠 **Future support** for editing existing blocks.

---

## 📋 Menu Options

Upon running the application, users can choose:

```
1. Create Block
2. Edit Block (Under Development)
3. Create Deadlock
```

---

## 🔨 Feature Descriptions

### 1️⃣ Create Block

After entering a name for the block, choose from:

| Option | Description                      |
| ------ | -------------------------------- |
| a      | Block for a specific time period |
| b      | Block starting after some delay  |
| c      | Set a daily usage time limit     |
| d      | Set a password lock for apps     |

🔧 This feature uses GUI prompts (e.g., `BlacklistGUI`) to select applications and define settings.

### 2️⃣ Edit Block

🚧 **Coming Soon**
Currently not implemented.

### 3️⃣ Create Deadlock

A more rigid blocking mechanism, where options include:

| Option | Description                            |
| ------ | -------------------------------------- |
| a      | Timer-based deadlock                   |
| b      | Delayed deadlock                       |
| c      | Daily limit deadlock (**Coming Soon**) |
| d      | Password-protected deadlock            |

Deadlocks are intended to be harder to reverse, increasing user discipline.

---

## 🚀 How to Run

### Requirements

* Java 8 or higher
* All GUI and utility classes present in the same project:

  * `BlacklistGUI`
  * `Applications`
  * `CountdownTimerGUI`
  * `DailyLimitLock`
  * `PasswordGUI`
  * `Deadlock`

### Steps

```bash
javac Main.java
java Main
```

---

## 📌 Notes

* GUI components are expected to be implemented for user interaction.
* Functionalities like `Edit Block` and `Daily Deadlock` are placeholders and will be added later.
* Make sure supporting classes (`Applications`, `Deadlock`, etc.) are compiled and accessible.

---

## 🎓 Educational Context

This project demonstrates:

* Java class modularity
* Use of GUI for file/application selection
* Integration of timers, input validation, and control flow
* Foundational project for productivity apps or parental control tools

---

## 📄 License

This project is open for educational use. Attribution is appreciated if reused or modified.
