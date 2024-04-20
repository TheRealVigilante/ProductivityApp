import javax.swing.*;
import java.io.IOException;
import java.lang.ProcessBuilder;
import java.time.LocalTime;
import java.time.format.DateTimeParseException;
import java.util.Scanner;

public class Deadlock {
    private String deadlockName;
    private LocalTime startTime;
    private LocalTime endTime;
    private boolean isActive;

    public Deadlock (String deadlockName, LocalTime startTime, LocalTime endTime, boolean isActive) {
        setDeadlockName(deadlockName);
        setStartTime(startTime);
        setEndTime(endTime);
        setActive(isActive);
        dailyDeadlock();
    }
    public void setDeadlockName(String deadlockName) {
        this.deadlockName = deadlockName;

    }

    public LocalTime getStartTime() {
        return startTime;
    }
    public void setStartTime(LocalTime startTime) {
        this.startTime = startTime;
    }

    public LocalTime getEndTime() {
        return endTime;
    }
    public void setEndTime(LocalTime endTime) {
        this.endTime = endTime;
    }

    public boolean isActive() {
        return isActive;
    }
    public void setActive(boolean active) {
        isActive = active;
    }
    public static void PassDeadlock(){
        PasswordGUI passwordGUI = new PasswordGUI();
        passwordGUI.launchGUI();
        passwordGUI.waitForSubmit();
        while (true){
            System.out.println("Deadlock is active");
            try {
                lockWorkstation();
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }
            try {
                Thread.sleep(1000); // Sleep for 1000 milliseconds (1 second)
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

        }

    }

    public static void TimerDeadlock(){
        Scanner scanner = new Scanner(System.in);
        System.out.println("Enter duration in hours:minutes:seconds (e.g., 2:30:00):");
        if (scanner.hasNextLine()) {
            String input = scanner.nextLine();
            String[] timeParts = input.split(":");
            if (timeParts.length != 3) {
                System.out.println("Invalid input format. Please enter in hours:minutes:seconds format.");
                scanner.close();
                return;
            }
            try {
                int hours = Integer.parseInt(timeParts[0]);
                int minutes = Integer.parseInt(timeParts[1]);
                int seconds = Integer.parseInt(timeParts[2]);

                SwingUtilities.invokeLater(new Runnable() {
                    public void run() {
                        new CountdownTimerGUI(hours, minutes, seconds).setVisible(true);
                    }
                });
                int tempSec = hours * 3600 + minutes * 60 + seconds;
                while (tempSec>=0){
                    System.out.println("Deadlock is active");
                    try {
                        lockWorkstation();
                    } catch (IOException | InterruptedException e) {
                        e.printStackTrace();
                    }
                    tempSec--;
                    try {
                        Thread.sleep(1000); // Sleep for 1000 milliseconds (1 second)
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
                System.exit(0);
            }
            catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter valid numbers.");
            }
            scanner.close();
        } else {
            System.out.println("No input provided.");
        }
    }
    public static void AfterTimerDeadlock(){
        CountdownTimerGUI.TimerSet();
        while (!CountdownTimerGUI.isMidnight()){
            System.out.println("Deadlock is active");
            try {
                lockWorkstation();
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }
            try {
                Thread.sleep(1000); // Sleep for 1000 milliseconds (1 second)
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
    public static void DailyDeadlock() throws InterruptedException, IOException {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Enter the start time in 24 hour format (hour:minute): ");
        String startTimeStr = scanner.nextLine();

        System.out.println("Enter the end time in 24 hour format (hour:minute): ");
        String endTimeStr = scanner.nextLine();
        LocalTime startTime = LocalTime.parse(startTimeStr);
        LocalTime endTime = LocalTime.parse(endTimeStr);

        try {

            System.out.println(startTime);
            System.out.println(endTime);
            while (true) {
                if (DailyLimitLock.isBefore(LocalTime.now(), startTime)) {
                    System.out.println("Before start time, please wait...");
                    Thread.sleep(10000);
                    System.out.println(LocalTime.now());
                } else {
                    // deadlock
                    while (!DailyLimitLock.isAfter(LocalTime.now(), endTime)) {
                        System.out.println("Inside prohibited time, apps are locked");
                        new Deadlock("Test", startTime, endTime, true);
                        Thread.sleep(30000);
                    }
                    System.out.println("Outside prohibited time, unlocking now");
                    break;
                }
            }
        } catch (DateTimeParseException e) {
            System.out.println("Invalid time format. Please use the format 'hour:minute'.");
        }
        scanner.close();
    }

    public void dailyDeadlock () {

        boolean greater_equal_startTime = (LocalTime.now().equals(getStartTime()) || LocalTime.now().isAfter(getStartTime()));
        boolean less_equal_endTime = (LocalTime.now().equals(getEndTime()) || LocalTime.now().isBefore(getEndTime()));


        while (greater_equal_startTime && less_equal_endTime && this.isActive()) {

            System.out.println("Deadlock is active");
            try {
                lockWorkstation();
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }

            try {
                Thread.sleep(1000); // Sleep for 1000 milliseconds (1 second)
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            greater_equal_startTime = (LocalTime.now().equals(getStartTime()) || LocalTime.now().isAfter(startTime));
            less_equal_endTime = (LocalTime.now().equals(getEndTime()) || LocalTime.now().isBefore(getEndTime()));
        }
    }

    private static void lockWorkstation() throws IOException, InterruptedException {
        String command = "rundll32.exe user32.dll,LockWorkStation";
        ProcessBuilder processBuilder = new ProcessBuilder(command.split(" "));
        Process process = processBuilder.start();

        // Wait for the process to complete
        int exitCode = process.waitFor();

        if (exitCode == 0) {
            System.out.println("Workstation locked successfully.");
        } else {
            System.out.println("Failed to lock the workstation. Exit code: " + exitCode);
        }
    }

}
