# Unreal Engine C++ Coffee Machine Setup Guide

## Step 1: Setting Up Your C++ Project

### Create New Project
1. Open Unreal Engine
2. Create new project using **Third Person** template
3. **CRITICAL**: Select **C++** as project type (not Blueprint)
4. Name your project (e.g., "CoffeeSimulation")
5. Click **Create**

### Copy C++ Files
1. Close Unreal Editor
2. Navigate to: `YourProject/Source/YourProject/`
3. Copy these files into that folder:
   - `SimulationCharacter.h`
   - `SimulationCharacter.cpp`
   - `CoffeeMachine.h`
   - `CoffeeMachine.cpp`
   - `InteractionComponent.h`
   - `InteractionComponent.cpp`

### Generate Project Files
1. Right-click `YourProject.uproject` file
2. Select **"Generate Visual Studio project files"**
3. Wait for completion

### Build Project
1. Open `YourProject.sln` in Visual Studio
2. Press **Ctrl+Shift+B** or go to **Build > Build Solution**
3. Wait for successful compilation
4. Close Visual Studio

### Reopen in Unreal
1. Double-click `YourProject.uproject`
2. Your C++ classes are now available

## Step 2: Configuring Player Character

### Update Blueprint Character
1. Open **BP_ThirdPersonCharacter** in Content Browser
2. Go to **Class Settings** (top toolbar)
3. Change **Parent Class** from `Character` to `SimulationCharacter`
4. Click **Compile** and **Save**

### Set Up Input Mappings
1. Go to **Edit > Project Settings**
2. Navigate to **Input > Action Mappings**
3. Add these mappings:
   - **Interact**: E key
   - **Grab**: G key (or F key)

## Step 3: Creating Coffee Machine

### Create Coffee Machine Blueprint
1. In Content Browser: **Right-click > Blueprint Class**
2. Search for **CoffeeMachine** (your C++ class)
3. Name it **BP_CoffeeMachine**
4. Open the Blueprint

### Set Up Coffee Machine
1. Add a **Static Mesh** component
2. Assign a coffee machine mesh (or basic cube)
3. Set **Interaction Sphere** radius to 200
4. **Compile** and **Save**

### Place in Level
1. Drag **BP_CoffeeMachine** into your level
2. Position where you want it

## Step 4: Creating UMG Widget (Coffee Prompt)

### Create Widget Blueprint
1. Content Browser: **Right-click > User Interface > Widget Blueprint**
2. Name it **WBP_CoffeePrompt**

### Design the Widget
1. Open **WBP_CoffeePrompt**
2. Add **Canvas Panel** to graph
3. Add **Border** inside Canvas Panel
4. Center the Border
5. Add **Vertical Box** inside Border
6. Add **3 Buttons** inside Vertical Box
7. Add **Text** to each button:
   - Button 1: "Brew Coffee"
   - Button 2: "Add Sugar" 
   - Button 3: "Cancel"

### Style the Widget
1. Set Border color (dark background)
2. Set Button colors
3. Set Text colors and fonts
4. **Compile** and **Save**

## Step 5: Connect Everything

### Link Widget to Coffee Machine
1. Open **BP_CoffeeMachine**
2. Select **Prompt Widget** component
3. Set **Widget Class** to **WBP_CoffeePrompt**
4. **Compile** and **Save**

### Test the System
1. Play the game
2. Walk near coffee machine
3. Press **E** to interact
4. Use **G** to grab objects

## Important Notes

- Replace `YOURPROJECTNAME` in all .h files with your actual project name
- Make sure to compile after each change
- Test frequently to catch issues early
- The interaction system uses line traces for detection

## Troubleshooting

**Build Errors**: Make sure all files are in correct folder and project name matches
**Widget Not Showing**: Check Widget Component settings in coffee machine
**Input Not Working**: Verify Action Mappings in Project Settings
**Character Not Moving**: Check Parent Class is set to SimulationCharacter

## Quick Commands

```bash
# Navigate to project folder
cd /path/to/your/project

# Generate project files (if needed)
# Right-click .uproject file instead

# Build project
# Use Visual Studio or Unreal Editor
```

Your coffee machine interaction system is now ready!