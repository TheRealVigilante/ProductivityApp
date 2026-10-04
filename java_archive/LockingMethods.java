import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.IOException;
import java.time.LocalTime;
import java.time.format.DateTimeParseException;
import java.util.Scanner;

class CountdownTimerGUI extends JFrame {
    private JLabel timerLabel;
    private Timer timer;
    private int durationInSeconds;

    public CountdownTimerGUI(int hours, int minutes, int seconds) {
        setTitle("Countdown Timer");
        setDefaultCloseOperation(JFrame.HIDE_ON_CLOSE);
        setSize(250, 200);
        setLayout(new FlowLayout());

        timerLabel = new JLabel();
        timerLabel.setFont(new Font("Arial", Font.PLAIN, 24));
        add(timerLabel);

        // Calculate duration in seconds from input
        durationInSeconds = hours * 3600 + minutes * 60 + seconds;

        startTimer();
    }

    private void startTimer() {
        timer = new Timer(1000, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if (durationInSeconds > 0) {
                    int hours = durationInSeconds / 3600;
                    int remainingSeconds = durationInSeconds % 3600;
                    int minutes = remainingSeconds / 60;
                    int seconds = remainingSeconds % 60;

                    String timerText = String.format("%02d:%02d:%02d", hours, minutes, seconds);
                    timerLabel.setText(timerText);
                    durationInSeconds--;
                } else {
                    timer.stop();
                    JOptionPane.showMessageDialog(CountdownTimerGUI.this, "Countdown Complete!");
                }
            }
        });
        timer.start();
    }

    public static void TimerSet(){
        // Get duration input from the terminal
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
                Timer(tempSec);
            }
            catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter valid numbers.");
            }
            scanner.close();
        } else {
            System.out.println("No input provided.");
        }
    }
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
    public static void Time(String[] files, String listName) throws IOException {
        if (Applications.isEmpty(files)){
            System.out.println("No files is selected, Try picking some first");
            return;
        }
        BlacklistGUI.lockWebsites(listName);
        Applications.LockApplications(files);
        CountdownTimerGUI.TimerSet();
        Applications.UnlockApplications(files);
        BlacklistGUI.unlockWebsites(listName);
//        do you want to do anything else? if yes, recurse main. if no, System.exit(0);
    }
    public static void AfterTime(String[] files, String listName) throws IOException {
        if (Applications.isEmpty(files)){
            System.out.println("No files is selected");
            return;
        }
        CountdownTimerGUI.TimerSet();
        BlacklistGUI.lockWebsites(listName);
        Applications.LockApplications(files);
        System.out.println("\nWait till midnight and it will reset");
        while (!isMidnight());
        BlacklistGUI.unlockWebsites(listName);
        Applications.UnlockApplications(files);
    }
}
class PasswordGUI extends JFrame {
    public String[] files;
    private final Object lock = new Object();
    private JTextField passwordField;
    private JButton setPasswordButton;
    private JButton submitButton;
    private String storedPassword;

    public PasswordGUI() {
        setTitle("Password Management");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(350, 200);
        setLayout(new FlowLayout());

        createSetPasswordGUI();
    }

    private void createSetPasswordGUI() {
        JLabel setPasswordLabel = new JLabel("Set Password:");
        add(setPasswordLabel);

        passwordField = new JPasswordField(20);
        add(passwordField);

        setPasswordButton = new JButton("Set Password");
        setPasswordButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                storedPassword = passwordField.getText();
                System.out.println("Password Set: " + storedPassword);
                passwordField.setText("");
                passwordField.setEnabled(true);
                setPasswordButton.setEnabled(false);
                Waiting();
            }
        });
        add(setPasswordButton);
    }
    private void Waiting() {
        SwingWorker<Void, Void> backgroundWorker = new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground() throws Exception {
                // Simulate background tasks for 3 seconds
                System.out.println("Please Wait....");
                Thread.sleep(3000);
                System.out.println("Ready..");
                return null;
            }

            @Override
            protected void done() {
                // After background tasks are done, enable password entry
                System.out.println("Allowing password entry now");
                getContentPane().removeAll();
                createEnterPasswordGUI();
                revalidate();
                repaint();
            }
        };
        backgroundWorker.execute();
    }
    private void createEnterPasswordGUI() {
        JLabel enterPasswordLabel = new JLabel("Enter Password:");
        add(enterPasswordLabel);

        passwordField = new JPasswordField(20);
        add(passwordField);

        submitButton = new JButton("Submit Password");
        submitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String enteredPassword = passwordField.getText();
                if (storedPassword != null && enteredPassword.equals(storedPassword)) {
                    System.out.println("Password Correct! Access Granted.");
                    dispose(); // Close the GUI window
                    synchronized (lock) {
                        lock.notify(); // Notify the waiting thread
                    }
                } else {
                    System.out.println("Incorrect Password! Access Denied.");
                }
                passwordField.setText("");
            }
        });
        add(submitButton);
    }
    public void waitForSubmit() {
        synchronized (lock) {
            try {
                lock.wait(); // Wait until the button is clicked
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public void launchGUI() {
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                setVisible(true);
            }
        });
    }
    public static void PasswordLock(String[] files,String listName) throws IOException {
        Applications.LockApplications(files);
        BlacklistGUI.lockWebsites(listName);
        PasswordGUI passwordGUI = new PasswordGUI();
        passwordGUI.launchGUI();
        passwordGUI.waitForSubmit();
        Applications.UnlockApplications(files);
        BlacklistGUI.unlockWebsites(listName);
    }
}
class DailyLimitLock {

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
