
import java.io.IOException;
import java.time.LocalTime;
import java.time.format.DateTimeParseException;
import java.util.Scanner;

public class DailyLimitLock {

    public static void DailyLock(String[] files,String listName) throws InterruptedException, IOException {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Enter the start time in 24 hour format (hour:minute): ");
        String startTimeStr = scanner.nextLine();

        System.out.println("Enter the end time in 24 hour format (hour:minute): ");
        String endTimeStr = scanner.nextLine();

        try {
            LocalTime startTime = LocalTime.parse(startTimeStr);
            LocalTime endTime = LocalTime.parse(endTimeStr);
            System.out.println(startTime);
            System.out.println(endTime);
            while (true) {
                if (isBefore(LocalTime.now(), startTime)) {
                    System.out.println("Before start time, please wait...");
                    Thread.sleep(10000);
                    System.out.println(LocalTime.now());
                }
                else {
                    Applications.LockApplications(files);
                    BlacklistGUI.lockWebsites(listName);
                    while (!isAfter(LocalTime.now(),endTime)){
                        System.out.println("Inside prohibited time, apps are locked");
                        Thread.sleep(30000);
                    }
                    System.out.println("Outside prohibited time, unlocking apps now");
                    Applications.UnlockApplications(files);
                    BlacklistGUI.unlockWebsites(listName);
                    break;
                }
            }
        } catch (DateTimeParseException e) {
            System.out.println("Invalid time format. Please use the format 'hour:minute'.");
        }
        scanner.close();
    }

    public static boolean isBefore(LocalTime currentTime, LocalTime startTime) {
        return currentTime.isBefore(startTime);
    }

    public static boolean isAfter(LocalTime currentTime, LocalTime endTime) {
        return currentTime.isAfter(endTime);
    }
}
