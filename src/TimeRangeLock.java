

import java.io.IOException;
import java.time.LocalTime;

public class TimeRangeLock {
    public static boolean isMidnight(){
        LocalTime currentTime = LocalTime.now();

        return currentTime.getHour() == 0 && currentTime.getMinute() == 0;

    }
    public static void Timer(long time) {
        time=time*1000;
        double extra=time*0.0061111;
        long l=(long) extra;
        time=time+l;
        try {
            Thread.sleep(time);// Sleep for the specified duration
        }
        catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }
    public static void Time(String[] files) throws IOException {
        if (Applications.isEmpty(files)){
            System.out.println("No files is selected, Try picking some first");
            return;
        }
        BlacklistGUI.lockWebsites();
        Applications.LockApplications(files);
        CountdownTimerGUI.TimerSet();
        Applications.UnlockApplications(files);
        BlacklistGUI.unlockWebsites();
//        do you want to do anything else? if yes, recurse main. if no, System.exit(0);
    }
    public static void AfterTime(String[] files) throws IOException {
        if (Applications.isEmpty(files)){
            System.out.println("No files is selected");
            return;
        }
        CountdownTimerGUI.TimerSet();
        BlacklistGUI.lockWebsites();
        Applications.LockApplications(files);
        System.out.println("\nWait till midnight and it will reset");
        while (!isMidnight());
        BlacklistGUI.unlockWebsites();
        Applications.UnlockApplications(files);
    }
    public static void TimeLock() throws IOException {
        BlacklistGUI blacklist = new BlacklistGUI();
        blacklist.launchGUI();
        blacklist.waitForSubmit();
        String[] files= Applications.AbsoluteFinder().toArray(new String[0]);
        Time(files);//0.611% error
    }
    public static void AfterTimeLock() throws IOException {
        BlacklistGUI blacklist = new BlacklistGUI();
        blacklist.launchGUI();
        blacklist.waitForSubmit();
        String[] files= Applications.AbsoluteFinder().toArray(new String[0]);
        AfterTime(files);
    }
}
