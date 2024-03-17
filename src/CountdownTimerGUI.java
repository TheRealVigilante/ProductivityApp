
import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Scanner;

public class CountdownTimerGUI extends JFrame {
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
            TimeRangeLock.Timer(tempSec);
        }
        catch (NumberFormatException e) {
            System.out.println("Invalid input. Please enter valid numbers.");
        }
        scanner.close();
    }
}