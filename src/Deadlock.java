

import java.io.IOException;
import java.lang.ProcessBuilder;
import java.time.LocalTime;
public class Deadlock {

    private String deadlockName;
//    private LocalTime startTime = LocalTime.of(8, 0, 0);    // 8:00 AM
//    private LocalTime endTime = LocalTime.of(17, 0, 0);
    private LocalTime startTime;
    private LocalTime endTime;
    private boolean isActive;
    // private String lockType;


    public Deadlock () {  }

    public Deadlock (String deadlockName, LocalTime startTime, LocalTime endTime, boolean isActive) {
        setDeadlockName(deadlockName);
        setStartTime(startTime);
        setEndTime(endTime);
        setActive(isActive);
        activeDeadlock();
    }

    public String getDeadlockName() {
        return deadlockName;
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


    public void activeDeadlock () {

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
