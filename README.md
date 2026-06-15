<div align="center">

<img src="https://readme-typing-svg.demolab.com/?font=Fira+Code&size=30&pause=1000&color=00D4FF&center=true&vCenter=true&width=500&lines=sms-spoofer" alt="Typing SVG" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Vonage](https://img.shields.io/badge/Powered%20by-Vonage%20API-C000C0?style=flat-square)](https://www.vonage.com/communications-apis/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-informational?style=flat-square)](https://github.com/Defaultik/sms_spoofer)
[![Stars](https://img.shields.io/github/stars/Defaultik/sms_spoofer?style=flat-square&color=yellow)](https://github.com/Defaultik/sms_spoofer/stargazers)
[![Forks](https://img.shields.io/github/forks/Defaultik/sms_spoofer?style=flat-square&color=orange)](https://github.com/Defaultik/sms_spoofer/network/members)

<br/>

**Utility to send SMS messages with a custom Sender ID**  
A clean CLI, Perfect for any use case where the sender name matters

[🐛 Report Bug](https://github.com/Defaultik/sms_spoofer/issues) / [💡 Request Feature](https://github.com/Defaultik/sms_spoofer/issues)

</div>

---

## 📸 Preview

> ![alt-text](https://i.imgur.com/zsosj2D.png)

---

## 📖 What is this?

`sms-spoofer` is a cross-platform Python utility that let you send SMS messages where the **Sender ID** (the name shown instead of a phone number) is fully customizable.

This is the same mechanism used by legitimate services worldwide — OTP codes, delivery notifications, appointment reminders, password resets, two-factor authentication prompts — all rely on custom Sender IDs.

> 📸 See it in action: [Example #1](https://i.imgur.com/SOmATqN.jpg) · [Example #2](https://i.imgur.com/Ll26s2U.jpg)

---

## ✨ Features

| Feature | Details |
|--------|---------|
| 🖥️ **Cross-Platform** | Runs natively on Windows, Linux, and macOS |
| 🎛️ **Menu-Based CLI** | Interactive terminal interface, no config files needed |
| 🐍 **Pure Python** | No compiled binaries, fully readable source code |
| 🗣️ **Unicode Support** | Works in English, Russian, Chinese, Arabic, and more |
| 🏷️ **Custom Sender ID** | Set any alphanumeric name as the sender (up to 11 chars) |
| 🌍 **Global Reach** | Send to virtually any country via Vonage's global network |

---

## 🚀 Quick Start

**Requirements:** Python 3.14+ (verified version), [Vonage account](https://ui.idp.vonage.com/ui/auth/registration)

```bash
# 1. Clone the repo
git clone https://github.com/Defaultik/sms-spoofer.git
cd sms-spoofer

# 3. Run
## Menu Based
python source/menu/main.py

## Command Based
python source/command/sms_spoofer.py
```

### Installing dependencies
<details><summary>pip</summary>
  
```bash
pip install -r requirements.txt
```
</details>

<details><summary>uv</summary>
  
```bash
uv sync
```
</details>

---

## 🎬 Usage

Once launched, you'll be greeted by an interactive menu. Simply:

1. Enter your **Vonage API Key** and **API Secret** (found in your [Vonage Dashboard](https://dashboard.nexmo.com/))
2. Specify the **Sender Name** (what the recipient will see instead of a number)
3. Enter the **recipient's phone number** in international format (e.g. `+1001234567`)
4. Type your **message**
5. Hit send ✉️

---

## ❓ FAQ

<details>
<summary><strong>Is this free?</strong></summary>

The tool itself is free and open-source, but **Vonage charges per SMS sent**. Pricing depends on the destination country. You can check [Vonage SMS Pricing](https://www.vonage.com/communications-apis/sms/pricing/) for details. New accounts receive a small free credit to get started.

</details>

<details>
<summary><strong>Which languages does it support?</strong></summary>

Full Unicode support — English, Russian, Chinese, Arabic, Hebrew, and all other Unicode-compatible languages work out of the box.

</details>

<details>
<summary><strong>Can my account get banned?</strong></summary>

Yes — if you violate [Vonage's Terms of Use](https://www.vonage.com/legal/communications-apis/terms-of-use/), your account may be suspended. Use this tool responsibly and only for legitimate purposes.

</details>

<details>
<summary><strong>Does it work on Linux?</strong></summary>

Yes, fully supported. The codebase is platform-agnostic and has been tested on both Windows and Linux environments.

</details>

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 [Open an issue](https://github.com/Defaultik/sms_spoofer/issues) for bugs or suggestions
- 🔀 Submit a Pull Request with improvements
- ⭐ Star the repo if you find it useful — it genuinely helps!

---

## ⚠️ Legal & Ethical Disclaimer

This utility relies entirely on the **official public Vonage API**. 

**The author assumes no liability for misuse.**

---

<div align="center">

I'll glad to get a star from you

Made with ❤️ by [Defaultik](https://github.com/Defaultik)

</div>
