import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

/**
 * StudyCompanionLauncher
 * 
 * A Java launcher that runs the AI Study Companion Python application
 * in the background. This is useful for integrating the Python app
 * into Java-based projects or systems.
 * 
 * @author AI Study Companion Team
 * @version 1.0
 */
public class StudyCompanionLauncher {
    
    private Process pythonProcess;
    private String projectPath;
    private String pythonCommand = "python3.11"; // Use Python 3.11 specifically
    
    /**
     * Constructor with default project path (current directory)
     */
    public StudyCompanionLauncher() {
        this.projectPath = System.getProperty("user.dir");
    }
    
    /**
     * Constructor with custom project path
     * @param projectPath The absolute path to the AI Study Companion project
     */
    public StudyCompanionLauncher(String projectPath) {
        this.projectPath = projectPath;
    }
    
    /**
     * Set the Python command (e.g., "python", "python3", or full path)
     * @param pythonCommand The Python executable command or path
     */
    public void setPythonCommand(String pythonCommand) {
        this.pythonCommand = pythonCommand;
    }
    
    /**
     * Automatically detect and set Python 3.11 if available
     * @return true if Python 3.11 was found, false otherwise
     */
    public boolean detectPython311() {
        String[] pythonCommands = {
            "python3.11",
            "python311",
            "py -3.11",
            "C:\\Python311\\python.exe",
            "C:\\Program Files\\Python311\\python.exe",
            "C:\\Users\\" + System.getProperty("user.name") + "\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
        };
        
        for (String cmd : pythonCommands) {
            try {
                ProcessBuilder pb = new ProcessBuilder(cmd.split(" "));
                pb.redirectErrorStream(true);
                Process p = pb.start();
                
                BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
                String version = reader.readLine();
                p.waitFor(2, java.util.concurrent.TimeUnit.SECONDS);
                p.destroy();
                
                if (version != null && version.contains("3.11")) {
                    this.pythonCommand = cmd;
                    System.out.println("✅ Found Python 3.11: " + cmd);
                    return true;
                }
            } catch (Exception e) {
                // Try next command
            }
        }
        
        System.err.println("⚠️  Python 3.11 not found, using: " + this.pythonCommand);
        return false;
    }
    
    /**
     * Launch the Python application in the background
     * @return true if launched successfully, false otherwise
     */
    public boolean launch() {
        try {
            // Auto-detect Python 3.11 if using default command
            if (pythonCommand.equals("python3.11") || pythonCommand.equals("python")) {
                detectPython311();
            }
            
            // Verify main.py exists
            File mainFile = new File(projectPath, "main.py");
            if (!mainFile.exists()) {
                System.err.println("Error: main.py not found at: " + mainFile.getAbsolutePath());
                return false;
            }
            
            System.out.println("🚀 Launching AI Study Companion...");
            System.out.println("📁 Project path: " + projectPath);
            System.out.println("🐍 Python command: " + pythonCommand);
            
            // Build the command
            List<String> command = new ArrayList<>();
            command.add(pythonCommand);
            command.add("main.py");
            
            // Create process builder
            ProcessBuilder processBuilder = new ProcessBuilder(command);
            processBuilder.directory(new File(projectPath));
            
            // Redirect error stream to output stream
            processBuilder.redirectErrorStream(true);
            
            // Start the process
            pythonProcess = processBuilder.start();
            
            // Create a thread to read output (prevents buffer overflow)
            Thread outputThread = new Thread(() -> {
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(pythonProcess.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        System.out.println("[Python] " + line);
                    }
                } catch (IOException e) {
                    if (!e.getMessage().contains("Stream closed")) {
                        System.err.println("Error reading Python output: " + e.getMessage());
                    }
                }
            });
            outputThread.setDaemon(true);
            outputThread.start();
            
            // Give it a moment to start
            Thread.sleep(1000);
            
            // Check if process is still running
            if (pythonProcess.isAlive()) {
                System.out.println("✅ AI Study Companion launched successfully!");
                System.out.println("📝 Process ID: " + pythonProcess.pid());
                return true;
            } else {
                System.err.println("❌ Python process terminated immediately");
                int exitCode = pythonProcess.exitValue();
                System.err.println("Exit code: " + exitCode);
                return false;
            }
            
        } catch (IOException e) {
            System.err.println("❌ Error launching Python application: " + e.getMessage());
            System.err.println("💡 Make sure Python is installed and in your PATH");
            return false;
        } catch (InterruptedException e) {
            System.err.println("❌ Launch interrupted: " + e.getMessage());
            Thread.currentThread().interrupt();
            return false;
        }
    }
    
    /**
     * Check if the Python application is currently running
     * @return true if running, false otherwise
     */
    public boolean isRunning() {
        return pythonProcess != null && pythonProcess.isAlive();
    }
    
    /**
     * Stop the Python application gracefully
     */
    public void stop() {
        if (pythonProcess != null && pythonProcess.isAlive()) {
            System.out.println("⏹️  Stopping AI Study Companion...");
            pythonProcess.destroy();
            
            try {
                // Wait up to 5 seconds for graceful shutdown
                if (!pythonProcess.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
                    System.out.println("⚠️  Force killing process...");
                    pythonProcess.destroyForcibly();
                }
                System.out.println("✅ AI Study Companion stopped");
            } catch (InterruptedException e) {
                System.err.println("Error waiting for process to stop: " + e.getMessage());
                pythonProcess.destroyForcibly();
                Thread.currentThread().interrupt();
            }
        }
    }
    
    /**
     * Get the exit code of the Python process (if terminated)
     * @return exit code, or -1 if still running or never started
     */
    public int getExitCode() {
        if (pythonProcess != null && !pythonProcess.isAlive()) {
            return pythonProcess.exitValue();
        }
        return -1;
    }
    
    /**
     * Main method for standalone execution
     * Demonstrates how to use the launcher
     */
    public static void main(String[] args) {
        // Parse command line arguments
        String projectPath = null;
        String pythonCmd = "python3.11";  // Default to Python 3.11
        
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--path") && i + 1 < args.length) {
                projectPath = args[i + 1];
                i++;
            } else if (args[i].equals("--python") && i + 1 < args.length) {
                pythonCmd = args[i + 1];
                i++;
            } else if (args[i].equals("--help")) {
                printHelp();
                return;
            }
        }
        
        // Create launcher
        StudyCompanionLauncher launcher;
        if (projectPath != null) {
            launcher = new StudyCompanionLauncher(projectPath);
        } else {
            launcher = new StudyCompanionLauncher();
        }
        
        launcher.setPythonCommand(pythonCmd);
        
        // Launch the application
        if (launcher.launch()) {
            System.out.println("\n🎯 AI Study Companion is now running in the background");
            System.out.println("💡 Press Ctrl+C to stop the application");
            
            // Add shutdown hook to stop Python process when Java exits
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                System.out.println("\n🛑 Shutting down...");
                launcher.stop();
            }));
            
            // Keep the Java process alive while Python runs
            try {
                while (launcher.isRunning()) {
                    Thread.sleep(1000);
                }
                
                int exitCode = launcher.getExitCode();
                if (exitCode != 0) {
                    System.err.println("❌ Python application exited with code: " + exitCode);
                    System.exit(exitCode);
                } else {
                    System.out.println("✅ Python application exited normally");
                }
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        } else {
            System.err.println("❌ Failed to launch AI Study Companion");
            System.exit(1);
        }
    }
    
    /**
     * Print usage help
     */
    private static void printHelp() {
        System.out.println("AI Study Companion Launcher");
        System.out.println("===========================");
        System.out.println();
        System.out.println("Usage: java StudyCompanionLauncher [options]");
        System.out.println();
        System.out.println("Options:");
        System.out.println("  --path <path>     Set the project directory path");
        System.out.println("  --python <cmd>    Set the Python command (default: python3.11)");
        System.out.println("  --help            Show this help message");
        System.out.println();
        System.out.println("Examples:");
        System.out.println("  java StudyCompanionLauncher");
        System.out.println("  java StudyCompanionLauncher --python python3.11");
        System.out.println("  java StudyCompanionLauncher --path \"C:\\Projects\\AI-Study-Companion\"");
        System.out.println("  java StudyCompanionLauncher --python \"C:\\Python311\\python.exe\"");
        System.out.println();
    }
}
